import pandas as pd
import joblib
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from app.services.db_service import get_connection


# ------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------

def evaluate_model():

    print("Loading dataset...")

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM loan_data ORDER BY RAND() LIMIT 3000000",
        conn
    )

    conn.close()

    # ------------------------------------------------
    # FEATURE ENGINEERING
    # ------------------------------------------------

    df["employment_type"] = df["employment_type"].map({
        "Salaried": 0,
        "Self-Employed": 1
    })

    X = df.drop(["default", "id"], axis=1)
    y = df["default"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # ------------------------------------------------
    # LOAD MODEL
    # ------------------------------------------------

    print("Loading model metadata...")

    model_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../saved_models")
    )

    metadata_path = os.path.join(model_dir, "model_metadata.json")

    if not os.path.exists(metadata_path):
        raise FileNotFoundError("model_metadata.json not found")

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    model_filename = metadata["current_model"]
    model_id = model_filename.replace(".pkl", "")

    model_path = os.path.join(model_dir, model_filename)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = joblib.load(model_path)

    print(f"Model loaded: {model_filename}")

    # ------------------------------------------------
    # PREDICTIONS
    # ------------------------------------------------

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    # ------------------------------------------------
    # METRICS
    # ------------------------------------------------

    acc = accuracy_score(y_test, preds)
    roc = roc_auc_score(y_test, probs)
    f1 = f1_score(y_test, preds)

    print("\nModel Evaluation Results")
    print("------------------------")
    print(f"Accuracy : {acc:.4f}")
    print(f"ROC-AUC  : {roc:.4f}")
    print(f"F1 Score : {f1:.4f}")

    report = classification_report(y_test, preds)

    # ------------------------------------------------
    # SAVE REPORTS
    # ------------------------------------------------

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    report_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../evaluation_reports",
            f"evaluation_{timestamp}"
        )
    )

    os.makedirs(report_dir, exist_ok=True)

    # Text Report
    report_path = os.path.join(report_dir, "classification_report.txt")

    with open(report_path, "w") as f:
        f.write(f"Model ID : {model_id}\n")
        f.write(f"Accuracy : {acc:.4f}\n")
        f.write(f"ROC-AUC  : {roc:.4f}\n")
        f.write(f"F1 Score : {f1:.4f}\n\n")
        f.write(report)

    # Confusion Matrix
    cm = confusion_matrix(y_test, preds)

    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")

    plt.title(f"Confusion Matrix ({model_id})")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    cm_path = os.path.join(report_dir, "confusion_matrix.png")

    plt.savefig(cm_path)
    plt.close()

    # ------------------------------------------------
    # OPTIONAL: SAVE TO DB (ADVANCED 🔥)
    # ------------------------------------------------

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE model_metadata
            SET accuracy=%s, f1_score=%s, roc_auc=%s
            WHERE model_id=%s
        """, (
            round(acc, 4),
            round(f1, 4),
            round(roc, 4),
            model_id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        print("Evaluation metrics updated in DB")

    except Exception as e:
        print(f"[WARNING] DB update failed: {e}")

    print("\nEvaluation saved successfully")
    print(f"Report folder: {report_dir}")


# ------------------------------------------------
# RUN SCRIPT
# ------------------------------------------------

if __name__ == "__main__":
    evaluate_model()