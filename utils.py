import json
import os

def load_users(filepath="data/users.json"):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as f:
        return json.load(f)

def save_users(filepath="data/users.json", data=None):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def load_trades(filepath="data/trades.json"):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return json.load(f)

def save_trades(filepath="data/trades.json", data=None):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def load_closed_trades(filepath="data/closed_trades.json"):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return json.load(f)

def save_closed_trades(data, filepath="data/closed_trades.json"):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
