
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
import joblib


def train():
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "..", "..", "data", "notebooks", "creditcard_clean.csv")
    df = pd.read_csv(data_path)

    X = df.drop("Class", axis=1)
    y = df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Modèles
    model_lr = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    )
    model_rf = RandomForestClassifier(
        n_estimators=100, max_depth=10, class_weight="balanced", random_state=42
    )
    model_mlp = make_pipeline(
        StandardScaler(),
        MLPClassifier(
            hidden_layer_sizes=(50, 50),
            max_iter=500,
            early_stopping=True,
            random_state=42,
        ),
    )

    model_lr.fit(X_train, y_train)
    model_rf.fit(X_train, y_train)
    model_mlp.fit(X_train, y_train)

    y_pred_lr = model_lr.predict(X_test)
    y_proba_lr = model_lr.predict_proba(X_test)
    y_pred_rf = model_rf.predict(X_test)
    y_proba_rf = model_rf.predict_proba(X_test)
    y_pred_mlp = model_mlp.predict(X_test)
    y_proba_mlp = model_mlp.predict_proba(X_test)

    print("LogisticRegression Metrics:")
    print(f"Precision: {precision_score(y_test, y_pred_lr):.4f}")
    print(f"Recall: {recall_score(y_test, y_pred_lr):.4f}")
    print(f"F1-Score: {f1_score(y_test, y_pred_lr):.4f}")
    print(f"ROC AUC: {roc_auc_score(y_test, y_proba_lr[:, 1]):.4f}")
    print()

    print("RandomForest Metrics:")
    print(f"Precision: {precision_score(y_test, y_pred_rf):.4f}")
    print(f"Recall: {recall_score(y_test, y_pred_rf):.4f}")
    print(f"F1-Score: {f1_score(y_test, y_pred_rf):.4f}")
    print(f"ROC AUC: {roc_auc_score(y_test, y_proba_rf[:, 1]):.4f}")
    print()

    print("MLP Metrics:")
    print(f"Precision: {precision_score(y_test, y_pred_mlp):.4f}")
    print(f"Recall: {recall_score(y_test, y_pred_mlp):.4f}")
    print(f"F1-Score: {f1_score(y_test, y_pred_mlp):.4f}")
    print(f"ROC AUC: {roc_auc_score(y_test, y_proba_mlp[:, 1]):.4f}")
    print()

    output_dir = os.path.join(base_dir, "..", "models")
    os.makedirs(output_dir, exist_ok=True)

    joblib.dump(model_rf, os.path.join(output_dir, "fraud_model.pkl"))

    print(f"Saved RandomForest model to {os.path.join(output_dir, 'fraud_model.pkl')}")


if __name__ == "__main__":
    train()
