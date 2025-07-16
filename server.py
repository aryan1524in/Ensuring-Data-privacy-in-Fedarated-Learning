import time
import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.server import ServerConfig


# Wait a bit for clients to connect
print("⏳ Waiting for clients to connect...")
time.sleep(5)  # Wait 5 seconds (you can increase if needed)

# Start server
fl.server.start_server(
    server_address="localhost:8080",
    config=ServerConfig(num_rounds=3),
    strategy=FedAvg(),
)
