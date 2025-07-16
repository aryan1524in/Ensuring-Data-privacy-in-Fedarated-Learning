import json
import os
from threading import Lock

METRICS_FILE = "metrics.json"
file_lock = Lock()

def save_metric(round_num, loss, accuracy, epsilon):
    new_entry = {
        "round": round_num,
        "loss": loss,
        "accuracy": accuracy,
        "epsilon": epsilon
    }

    with file_lock:
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append(new_entry)

        with open(METRICS_FILE, "w") as f:
            json.dump(data, f, indent=2)
