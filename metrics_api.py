from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# Enable CORS so frontend can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to 'http://localhost:5173' if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/metrics")
def get_metrics():
    if not os.path.exists("metrics.json"):
        return []
    with open("metrics.json", "r") as f:
        return json.load(f)
