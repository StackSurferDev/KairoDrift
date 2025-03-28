# /ml/train_model.py - Simons Town & Cape Point Drift Model Trainer

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# === Simulate dummy drift logs for Simon's Town & Cape Point ===
def generate_simons_town_data(samples=500):
    np.random.seed(42)
    person_profiles = [
        ("Person_Adult_LifeJacket", 1.0),
        ("Person_Adult_NoLifeJacket", 1.1),
        ("Person_Adolescent_LifeJacket", 0.9),
        ("Person_Child_LifeJacket", 1.0)
    ]
    boat_profiles = [
        ("Catamaran", 0.4),
        ("Hobby_Cat", 0.5),
        ("Fishing_Trawler", 0.2),
        ("RHIB", 0.6),
        ("SUP_Board", 1.2),
        ("Windsurfer", 1.3),
        ("Kayak", 1.1)
    ]
    patterns = ["Sector Search", "Expanding Square", "Parallel Sweep"]

    data = []
    for _ in range(samples):
        if np.random.rand() < 0.4:
            obj, drag = person_profiles[np.random.randint(len(person_profiles))]
        else:
            obj, drag = boat_profiles[np.random.randint(len(boat_profiles))]

        lat = np.random.uniform(-34.35, -34.25)
        lon = np.random.uniform(18.45, 18.55)
        hours = np.random.uniform(0.5, 6.0)
        uo = np.random.uniform(0.2, 1.2)
        vo = np.random.uniform(0.2, 1.2)

        drift_km = ((uo * 3.6 * hours * drag)**2 + (vo * 3.6 * hours * drag)**2)**0.5

        if hours < 1.5 and drift_km < 2:
            pattern = "Sector Search"
        elif hours < 3.5:
            pattern = "Expanding Square"
        else:
            pattern = "Parallel Sweep"

        data.append([obj, lat, lon, hours, uo, vo, drag, drift_km, pattern])

    df = pd.DataFrame(data, columns=[
        "object_type", "latitude", "longitude", "hours_since",
        "uo", "vo", "drag", "drift_distance_km", "search_pattern"
    ])
    return df

# === Train models ===
def train_models():
    df = generate_simons_town_data()

    # Encode object and search pattern
    le_obj = LabelEncoder()
    df["object_code"] = le_obj.fit_transform(df["object_type"])
    joblib.dump(le_obj, "ml/object_encoder.pkl")

    le_pat = LabelEncoder()
    df["pattern_code"] = le_pat.fit_transform(df["search_pattern"])
    joblib.dump(le_pat, "ml/pattern_encoder.pkl")

    features = ["object_code", "drag", "hours_since", "uo", "vo"]

    # Regressor for drift km
    X = df[features]
    y_drift = df["drift_distance_km"]
    drift_model = RandomForestRegressor(n_estimators=100, random_state=42)
    drift_model.fit(X, y_drift)
    joblib.dump(drift_model, "ml/model_drift.pkl")

    # Classifier for pattern
    y_pattern = df["pattern_code"]
    pattern_model = RandomForestClassifier(n_estimators=100, random_state=42)
    pattern_model.fit(X, y_pattern)
    joblib.dump(pattern_model, "ml/model_pattern.pkl")

    print("✅ Models trained on Simon's Town & Cape Point data and saved in /ml/")

if __name__ == "__main__":
    os.makedirs("ml", exist_ok=True)
    train_models()
