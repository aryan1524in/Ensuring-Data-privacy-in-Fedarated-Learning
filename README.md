# Ensuring Data Privacy in Federated Learning

*A cloud-deployed, end-to-end system demonstrating privacy-preserving machine learning using Federated Learning, Differential Privacy, and AWS.*

---

## 1. Project Overview

This project addresses a critical challenge in modern AI: *how can we collaboratively train a machine learning model on sensitive, decentralized data without compromising individual privacy?*

We demonstrate a complete, functional solution by building a system that trains a neural network on the Wisconsin Breast Cancer dataset. The architecture ensures that raw data never leaves the client device, and mathematical guarantees of privacy are enforced through Differential Privacy. The entire system—from the federated server to the live metrics dashboard—is deployed on Amazon Web Services (AWS), showcasing a real-world, scalable implementation.

**Final Deployed Frontend:**  
[Dashboard link](http://f2-frontend-ibm.s3-website.ap-south-1.amazonaws.com/)

![Screenshot of Final Frontend Graph](/images/Screenshot%202025-07-23%20234033.png)

---

## 2. Core Concepts

### Federated Learning (FL)

Instead of pooling sensitive data into a central server, the model is sent to the data.

**Analogy:** Imagine a group of hospitals wanting to build a better diagnostic model. Instead of sharing confidential patient records, a central coordinator sends a copy of the AI model to each hospital. Each hospital trains the model on its own private data and sends back only the mathematical learnings (model updates). The coordinator then averages these learnings to create a smarter, global model.

**Implementation:** We use the *Flower (flwr)* framework to manage this process, with a central server orchestrating the training rounds with multiple clients.

---

### Differential Privacy (DP)

Provides strong, mathematical guarantees that the contribution of any single individual is protected.

**Analogy:** After each hospital trains its model, it adds a carefully calibrated amount of statistical "noise" to the learnings before sending them back. This noise makes it mathematically impossible for an attacker to reverse-engineer the updates to learn anything about a specific patient.

**Implementation:** We use the *Opacus* library from PyTorch. It automatically adds noise and clips the influence of individual data points, providing a measurable privacy guarantee known as *epsilon (ε)*. A lower epsilon means stronger privacy.

---

## 3. System Architecture

The project is composed of three main parts:

```plaintext
[ FL Clients ]  --> Train on local data using Opacus and send updates
        |
        v
[ FL Server ]  --> Aggregates updates using FedAvg
        |
        v
[ Metrics Writer ] --> Stores performance + ε to S3
        |
        v
[ FastAPI Metrics API ] --> Reads metrics from S3
        |
        v
[ React Frontend ] --> Displays graph of training progress
```
![Diagram](/images/working%20flow.png)

### Components:

1. **Federated Learning Backend:**
    - `server.py` — Orchestrates the training process.
    - `client.py` — Simulates client training with Differential Privacy.

2. **Metrics & Monitoring:**
    - `metrics_writer.py` — Writes training results and ε to Amazon S3.
    - `metrics_api.py` — FastAPI server that aggregates metrics from S3.

3. **Frontend Dashboard:**
    - A modern web application built with *React and Vite*.
    - It fetches the combined data from the Metrics API and renders a real-time graph visualizing the training progress, showing how accuracy, loss, and epsilon change over the federated rounds.
---

## 4. AWS Cloud Deployment Architecture

We deploy this architecture fully on AWS:

### ✅ Amazon EC2 (Elastic Compute Cloud)
- Hosts: `server.py`, `client.py`, and `metrics_api.py`
- **Config:**
  - t3.micro instance
  - 30 GB EBS volume
  - 2 GB swap file to handle PyTorch installs

### ✅ Amazon S3 (Simple Storage Service)
- *metrics-bucket:* for JSON logs of each client
- *frontend-bucket:* static site hosting for React dashboard

### ✅ Amazon KMS (Key Management Service)
- Encrypts all client metric files with a custom KMS key

### ✅ AWS IAM (Identity and Access Management)
- Role: `FlowerProjectEC2Role`
- Grants EC2 permission to write to S3 and use KMS

### ✅ Security Groups
- Open ports:
  - `22` – SSH
  - `8080` – FL server
  - `8000` – FastAPI API

---

## 5. How to Run This Project

### 🧱 Prerequisites
- Python 3.8+
- Node.js & npm
- AWS account with configured CLI or web console access

---

### 🔧 Local Setup

```bash
# Clone the repo
git clone <https://github.com/aryan1524in/Ensuring-Data-privacy-in-Fedarated-Learning.git>
cd <Ensuring-Data-privacy-in-Fedarated-Learning>
```

#### 📦 Backend Setup

```bash
cd Ensuring-Data-privacy-in-Fedarated-Learning/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 🌐 Frontend Setup

```bash
cd frontend-dashboard/
npm install
```

#### 🚀 Run Locally

```bash
# Terminal 1
python server.py

# Terminal 2+
python client.py  # run for each client

# Terminal 3
uvicorn metrics_api:app --port 8000

# Terminal 4
npm run dev  # inside frontend-dashboard/
```

---

### ☁️ AWS Deployment (Summary)

1. **Create IAM Role** `FlowerProjectEC2Role`  
   - Attach `AmazonS3FullAccess` + `KMS` access policies

2. **Create KMS Key**  
   - Allow your IAM role to use it

3. **Launch EC2 Instance**  
   - Use t3.micro
   - Add `30 GB` storage
   - Configure `security group` for ports 22, 8080, 8000
   - Attach the IAM role

4. **SSH into EC2 and Setup**
```bash
# Create 2 GB swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

5. **Clone repo and setup backend/frontend on EC2**

6. **Create S3 Buckets**
   - One for metrics (private)
   - One for frontend (public)
   - Enable *Static Website Hosting*

7. **Update Code Configs**
   - Add bucket name and KMS ARN to `metrics_writer.py` and `metrics_api.py`
   - In React, set API URL to EC2 public IP

8. **Run Backend Services with `tmux`**
```bash
tmux new -s server
python server.py

tmux new -s client1
python client.py

tmux new -s api
uvicorn metrics_api:app --host 0.0.0.0 --port 8000
```

9. **Build Frontend and Upload to S3**

```bash
cd frontend-dashboard/
npm run build

# Upload contents of /dist to the S3 bucket
```

10. **Enable Public Access**
   - Set the bucket policy to allow read access

---

## 6. Project in Action

### 🔧 EC2 tmux Running All Clients and Server
![ Screenshot](/images/Server-client.jpg)

<!-- ### 📁 S3 Bucket with Client Metrics
![S3 bucket screenshot](#)

### 🔒 Metrics File with KMS Encryption
![KMS encryption screenshot](#) -->

---

## 7. Conclusion & Future Work

By combining federated learning, differential privacy, and a robust cloud architecture, we've built more than a demo—we've built a vision for the future of intelligent, privacy-first systems.

### 🛠 Future Improvements:
- **Migrate to DynamoDB:** for scalable metrics retrieval
- **Containerization:** Use Docker + Amazon ECS
- **CI/CD Automation:** Deploy via GitHub Actions to S3

---
