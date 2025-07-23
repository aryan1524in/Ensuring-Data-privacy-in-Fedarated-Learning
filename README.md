# Ensuring Data Privacy in Federated Learning

*A cloud-deployed, end-to-end system demonstrating privacy-preserving machine learning using Federated Learning, Differential Privacy, and AWS.*

---

## 1. Project Overview

This project addresses a critical challenge in modern AI: *how can we collaboratively train a machine learning model on sensitive, decentralized data without compromising individual privacy?*

We demonstrate a complete, functional solution by building a system that trains a neural network on the Wisconsin Breast Cancer dataset. The architecture ensures that raw data never leaves the client device, and mathematical guarantees of privacy are enforced through Differential Privacy. The entire system—from the federated server to the live metrics dashboard—is deployed on Amazon Web Services (AWS), showcasing a real-world, scalable implementation.

*Final Deployed Frontend:*
You can link to your live S3 website here.

[INSERT SCREENSHOT OF THE FINAL DEPLOYED WEBSITE WITH THE GRAPH HERE]

---

## 2. Core Concepts

Our solution is built on two foundational privacy-enhancing technologies:

### Federated Learning (FL)
Instead of pooling sensitive data into a central server, the model is sent to the data.

* *Analogy:* Imagine a group of hospitals wanting to build a better diagnostic model. Instead of sharing confidential patient records, a central coordinator sends a copy of the AI model to each hospital. Each hospital trains the model on its own private data and sends back only the mathematical learnings (model updates). The coordinator then averages these learnings to create a smarter, global model.
* *Implementation:* We use the *Flower (flwr)* framework to manage this process, with a central server orchestrating the training rounds with multiple clients.

### Differential Privacy (DP)
This provides a strong, mathematical guarantee that the contribution of any single individual is protected.

* *Analogy:* After each hospital trains its model, it adds a carefully calibrated amount of statistical "noise" to the learnings before sending them back. This noise makes it mathematically impossible for an attacker to reverse-engineer the updates to learn anything about a specific patient.
* *Implementation:* We use the *Opacus* library from PyTorch, which seamlessly integrates into the training loop. It automatically adds noise and clips the influence of individual data points, providing a measurable privacy guarantee known as *epsilon ($\epsilon$)*. A lower epsilon means stronger privacy.

---

## 3. System Architecture

The project is composed of three main parts that work in concert: the FL Backend, the Metrics Pipeline, and the Frontend Dashboard.

[INSERT A SIMPLE ARCHITECTURE DIAGRAM HERE IF YOU HAVE ONE]

1.  *Federated Learning Backend:*
    * **FL Server (server.py):** A central server that orchestrates the training process. It initializes the global model, selects clients for each round, sends them the model, and aggregates their returned updates using the Federated Averaging (FedAvg) strategy.
    * **FL Clients (client.py):** These simulate end-user devices or data silos. Each client receives the global model, trains it on its local private data with Differential Privacy enabled, and sends the protected update back to the server.

2.  *Metrics & Monitoring Pipeline:*
    * **Metrics Writer (metrics_writer.py):** As each client trains, this module is responsible for saving the performance metrics (loss, accuracy) and the privacy cost ($\epsilon$) for that round.
    * *Storage (Amazon S3):* To handle multiple clients writing simultaneously without overwriting data, each client saves its metrics to a unique, separate file in an S3 bucket.
    * **Metrics API (metrics_api.py):** A FastAPI server that provides a public REST endpoint. When requested, it reads all the individual metric files from the S3 bucket, combines them into a single list, and sends them to the frontend.

3.  *Frontend Dashboard:*
    * A modern web application built with *React and Vite*.
    * It fetches the combined data from the Metrics API and renders a real-time graph visualizing the training progress, showing how accuracy, loss, and epsilon change over the federated rounds.

---

## 4. AWS Cloud Deployment Architecture

This project is not just a local script; it is fully deployed on AWS, demonstrating a scalable and secure cloud architecture.

* *Amazon EC2 (Elastic Compute Cloud):* Serves as the backbone of our compute infrastructure. We use t3.micro instances to run the FL Server, FL Clients, and the Metrics API. Key configurations include:
    * *30 GB EBS Volume:* The default 8 GB storage was increased to 30 GB to accommodate large ML libraries like PyTorch.
    * *Swap File:* A 2 GB swap file was configured to provide virtual RAM, preventing the Killed error caused by low memory during package installation.

* *Amazon S3 (Simple Storage Service):* Used for two critical functions:
    * *Metrics Storage:* As the durable, scalable storage for all individual JSON metric files generated by the clients.
    * *Static Website Hosting:* Hosts the production build of our React frontend, making it publicly accessible on the web at low cost and high reliability.

* *Amazon KMS (Key Management Service):* Provides an essential layer of security.
    * A customer-managed key was created to encrypt the metrics files stored in S3. This ensures that the data is encrypted at rest with a key that we control, providing a strong, auditable security posture.

* *AWS IAM (Identity and Access Management):* Manages secure access between services.
    * An IAM Role (FlowerProjectEC2Role) was created and attached to our EC2 instances. This role grants the instances the necessary permissions to write to S3 and use the KMS key, without ever storing secret keys in the code.

* *Security Groups:* Acts as a virtual firewall for our EC2 instances, configured to allow inbound traffic on the necessary ports:
    * *Port 22:* For SSH access.
    * *Port 8080:* For client-server communication via Flower.
    * *Port 8000:* For public access to our FastAPI metrics server.

---

## 5. How to Run This Project

### Prerequisites
* Python 3.8+
* Node.js and npm
* An AWS Account

### Local Setup
1.  *Clone the repository:*
    bash
    git clone <your-repo-url>
    cd <project-directory>
    
2.  *Backend Setup:*
    bash
    # Navigate to the backend folder
    cd privacy-federated/ 
    
    # Create and activate a virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install Python dependencies
    pip install -r requirements.txt
    
3.  *Frontend Setup:*
    bash
    # Navigate to the frontend folder
    cd frontend-dashboard/
    
    # Install Node dependencies
    npm install
    
4.  *Run Locally:*
    * Run the FL Server: python server.py
    * Run one or more FL Clients: python client.py
    * Run the API: uvicorn metrics_api:app --port 8000
    * Run the Frontend: npm run dev

### AWS Deployment (Summarized)
1.  *Create an IAM Role* (FlowerProjectEC2Role) with AmazonS3FullAccess and AmazonDynamoDBFullAccess permissions.
2.  *Create a KMS Key* and give the FlowerProjectEC2Role usage permissions.
3.  *Launch an EC2 Instance* (t3.micro), attaching the IAM role, configuring a security group for ports 22, 8080, and 8000, and increasing the storage to 30 GB.
4.  *Connect via SSH* and configure a swap file to prevent memory errors.
5.  *Clone the repo* and install dependencies inside a Python virtual environment.
6.  *Create an S3 Bucket* for metrics and another for the frontend, disabling "Block all public access" for the frontend bucket.
7.  *Update the Python scripts* (metrics_writer.py, metrics_api.py) with your S3 bucket name and KMS key ARN.
8.  *Update the React code* with the public IP of your EC2 instance.
9.  *Run the backend services* (server.py, client.py, metrics_api.py) on EC2 using tmux.
10. *Build the React app* (npm run build) and upload the contents of the dist folder to the frontend S3 bucket.
11. *Enable Static Website Hosting* on the frontend S3 bucket and set the bucket policy to allow public reads.

---

## 6. Project in Action

Here are some screenshots from the deployed AWS environment.

**The tmux session on EC2 showing the server, clients, and API running simultaneously:**

[INSERT YOUR TMUX SCREENSHOT HERE]

*The S3 bucket containing the individual metric files written by each client:*

[INSERT S3 BUCKET SCREENSHOT HERE]

*The KMS encryption details for a metrics file in S3, showing it's protected by our custom key:*

[INSERT S3 KMS ENCRYPTION SCREENSHOT HERE]

---

## 7. Conclusion and Future Work

This project successfully demonstrates a complete, end-to-end MLOps pipeline for privacy-preserving machine learning on the cloud. It proves that it is feasible to build powerful AI models that respect user privacy by design, moving from theoretical concepts to a practical, deployed application.

*Future Improvements:*
* *Migrate to DynamoDB:* For enhanced performance and scalability, the metrics storage could be migrated from individual S3 files to an Amazon DynamoDB table.
* *Containerization:* The backend services could be containerized using Docker and orchestrated with Amazon ECS for easier management and deployment.
* *CI/CD Automation:* A CI/CD pipeline using GitHub Actions could be implemented to automatically build and deploy the frontend to S3 on every code change.