import pandas as pd
import os
import joblib
import json
import re
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
from xgboost import XGBClassifier

from app.services.db_service import get_connection


# ------------------------------------------------
# MAIN TRAIN FUNCTION (IMPORTANT)
# ------------------------------------------------

def train_model():

    print("\nLoading dataset from database...")

    conn = get_connection()
    query = "SELECT * FROM loan_data ORDER BY RAND() LIMIT 3000000"
    df = pd.read_sql(query, conn)
    conn.close()

    print(f"Dataset loaded: {len(df)} rows")

    # ------------------------------------------------
    # FEATURE ENGINEERING
    # ------------------------------------------------

    df["employment_type"] = df["employment_type"].map({
        "Salaried": 0,
        "Self-Employed": 1
    })

    X = df.drop(["default", "id"], axis=1)
    y = df["default"]

    # ------------------------------------------------
    # SPLIT
    # ------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # ------------------------------------------------
    # MODELS
    # ------------------------------------------------

    print("\nTraining models...\n")

    best_model = None
    best_model_name = None
    best_roc = 0
    best_accuracy = 0
    best_f1 = 0

    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000),
        "RandomForest": RandomForestClassifier(
            n_estimators=250,
            max_depth=12,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            eval_metric="logloss",
            random_state=42,
            n_estimators=200,
            max_depth=6
        )
    }

    for name, model in models.items():

        print(f"Training {name}")

        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, preds)
        roc = roc_auc_score(y_test, probs)
        f1 = f1_score(y_test, preds)

        print(f"Accuracy : {acc:.4f}")
        print(f"ROC-AUC  : {roc:.4f}")
        print(f"F1 Score : {f1:.4f}")
        print("-" * 40)

        if roc > best_roc:
            best_model = model
            best_model_name = name
            best_accuracy = acc
            best_roc = roc
            best_f1 = f1

    # ------------------------------------------------
    # VERSIONING
    # ------------------------------------------------

    model_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../saved_models")
    )
    os.makedirs(model_dir, exist_ok=True)

    existing_models = [
        f for f in os.listdir(model_dir)
        if re.match(r"loan_model_v\d+\.pkl", f)
    ]

    if existing_models:
        versions = [int(re.search(r"v(\d+)", m).group(1)) for m in existing_models]
        version = max(versions) + 1
    else:
        version = 1

    # IMPORTANT: model_id = filename without .pkl
    model_id = f"loan_model_v{version}"
    model_filename = f"{model_id}.pkl"
    model_path = os.path.join(model_dir, model_filename)

    joblib.dump(best_model, model_path)

    print(f"\nBest Model: {best_model_name}")
    print(f"Model Saved: {model_filename}")

    # ------------------------------------------------
    # SAVE JSON METADATA
    # ------------------------------------------------

    metadata = {
        "current_model": model_filename,
        "algorithm": best_model_name,
        "training_date": str(datetime.now().date()),
        "accuracy": round(best_accuracy, 4),
        "roc_auc": round(best_roc, 4),
        "f1_score": round(best_f1, 4)
    }

    with open(os.path.join(model_dir, "model_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    print("Metadata JSON updated")

    # ------------------------------------------------
    # SAVE TO DATABASE (FIXED)
    # ------------------------------------------------

    print("Saving metadata to database...")

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO model_metadata
    (model_id, model_name, algorithm_type, accuracy, f1_score, roc_auc, version, training_time)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, (
        model_id,
        model_filename,
        best_model_name,
        round(best_accuracy, 4),
        round(best_f1, 4),
        round(best_roc, 4),
        version,
        datetime.now()
    ))

    conn.commit()
    cursor.close()
    conn.close()

    print("Metadata saved to database")
    print("\nTraining pipeline completed successfully")


# ------------------------------------------------
# RUN SCRIPT
# ------------------------------------------------

if __name__ == "__main__":
    train_model()