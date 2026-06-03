# Prediction logic
import joblib
import numpy as np
import pandas as pd
import os
base_dir = os.path.dirname(__file__)
model = joblib.load(os.path.join(base_dir, "..", "models", "fraud_model.pkl"))
def predict_fraude(transaction):
    return model.predict([transaction])

def predict_proba_fraude(transaction):
    return model.predict_proba([transaction])