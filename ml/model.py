import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from pymongo import MongoClient
import numpy as np
import config
import os

MODEL_PATH = "ml/trained_model.pkl"

def fetch_data():
    client = MongoClient(config.MONGO_URI)
    db = client["caterpillar"]
    collection = db["task_history"]

    data = list(collection.find({}))
    features = []
    targets = []

    for d in data:
        try:
            features.append([
                float(d.get("engine_hours", 0)),
                float(d.get("fuel_used", 0)),
                int(d.get("load_cycles", 0)),
                int(d.get("temperature", 0)),
                int(d.get("wind_speed", 0)),
                int(d.get("humidity", 0)),
            ])
            targets.append(float(d.get("task_time", 0)))
        except Exception as e:
            continue

    return np.array(features), np.array(targets)

def train_model():
    X, y = fetch_data()
    if len(X) < 10:
        raise Exception("Not enough data to train the model")

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    return "Model trained and saved!"

def load_model():
    if not os.path.exists(MODEL_PATH):
        train_model()
    return joblib.load(MODEL_PATH)
