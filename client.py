import flwr as fl
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from opacus import PrivacyEngine
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import TensorDataset, DataLoader
from metrics_writer import save_metric  # ✅

# 1. Load dataset
print("🔄 Loading Breast Cancer dataset...")
data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.long)

train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
test_dataset = TensorDataset(X_test_tensor, y_test_tensor)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32)

print("✅ Data loaded.")

# 2. Define model
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(30, 64)
        self.fc2 = nn.Linear(64, 2)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return self.fc2(x)

# 3. Federated Client
class FlowerClient(fl.client.NumPyClient):
    def __init__(self):
        self.model = Net()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.SGD(self.model.parameters(), lr=0.01)
        self.privacy_engine = PrivacyEngine()
        self.model, self.optimizer, train_loader_with_dp = self.privacy_engine.make_private(
            module=self.model,
            optimizer=self.optimizer,
            data_loader=train_loader,
            noise_multiplier=1.0,
            max_grad_norm=1.0,
        )
        self.train_loader = train_loader_with_dp
        self.round = 1  # ✅ Track training round

    def get_parameters(self, config=None):
        return [val.detach().cpu().numpy() for val in self.model.parameters()]

    def set_parameters(self, parameters):
        for param, new_val in zip(self.model.parameters(), parameters):
            param.data = torch.tensor(new_val, dtype=param.data.dtype, device=self.device)

    def fit(self, parameters, config):
        print(f"📡 Received fit request from server. Round {self.round}")
        self.set_parameters(parameters)

        self.model.train()
        total_loss = 0.0
        for x_batch, y_batch in self.train_loader:
            x_batch, y_batch = x_batch.to(self.device), y_batch.to(self.device)
            self.optimizer.zero_grad()
            outputs = self.model(x_batch)
            loss = self.criterion(outputs, y_batch)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(self.train_loader)
        epsilon = self.privacy_engine.get_epsilon(delta=1e-5)

        # Evaluate accuracy on test set
        self.model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for x_batch, y_batch in test_loader:
                x_batch, y_batch = x_batch.to(self.device), y_batch.to(self.device)
                outputs = self.model(x_batch)
                pred = outputs.argmax(dim=1)
                correct += pred.eq(y_batch).sum().item()
                total += y_batch.size(0)
        accuracy = correct / total

        print(f"🧠 Epoch 1 | 🔻 Avg Loss: {avg_loss:.4f}")
        print(f"🔒 Differential Privacy ε (Epsilon): {epsilon:.4f}")
        print(f"✅ Accuracy: {accuracy:.4f}")

        # ✅ Save metrics
        save_metric(self.round, avg_loss, accuracy, epsilon)
        self.round += 1

        print("📤 Sending updated model back to server.")
        return self.get_parameters(), len(self.train_loader.dataset), {}

    def evaluate(self, parameters, config):
        print("🧪 Received evaluation request from server.")
        self.set_parameters(parameters)

        self.model.eval()
        loss = 0.0
        correct = 0
        with torch.no_grad():
            for x_batch, y_batch in test_loader:
                x_batch, y_batch = x_batch.to(self.device), y_batch.to(self.device)
                outputs = self.model(x_batch)
                loss += self.criterion(outputs, y_batch).item()
                pred = outputs.argmax(dim=1)
                correct += pred.eq(y_batch).sum().item()

        loss /= len(test_loader)
        accuracy = correct / len(test_loader.dataset)
        print(f"✅ Evaluation — Loss: {loss:.4f} | Accuracy: {accuracy:.4f}")
        return float(loss), len(test_loader.dataset), {"accuracy": float(accuracy)}

# 4. Start Client
print("🚀 Starting Federated Client...")
fl.client.start_numpy_client(server_address="localhost:8080", client=FlowerClient())
