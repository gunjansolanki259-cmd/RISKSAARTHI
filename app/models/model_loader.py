import joblib
import os
import json
from app.services.db_service import get_connection

# ------------------------------------------------
# Paths
# ------------------------------------------------

BASE_DIR = os.path.dirname(__file__)

MODEL_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "../../ml/saved_models")
)

METADATA_PATH = os.path.join(MODEL_DIR, "model_metadata.json")


# ------------------------------------------------
# Helper: Load model from file
# ------------------------------------------------

def _load_model_file(model_file: str):

    model_path = os.path.join(MODEL_DIR, model_file)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    return joblib.load(model_path)


# ------------------------------------------------
# Helper: Load from JSON
# ------------------------------------------------

def _load_from_json():

    if not os.path.exists(METADATA_PATH):
        return None, None

    try:
        with open(METADATA_PATH, "r") as f:
            metadata = json.load(f)

        model_file = metadata.get("current_model")

        if model_file:
            model = _load_model_file(model_file)
            model_id = model_file.replace(".pkl", "")
            return model, model_id

    except Exception as e:
        print(f"[WARNING] JSON loading failed: {e}")

    return None, None


# ------------------------------------------------
# Helper: Load from Database
# ------------------------------------------------

def _load_from_db():

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT model_id
            FROM model_metadata
            ORDER BY training_time DESC
            LIMIT 1
        """)

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            model_id = result[0]
            model_file = f"{model_id}.pkl"
            model = _load_model_file(model_file)
            return model, model_id

    except Exception as e:
        print(f"[WARNING] DB loading failed: {e}")

    return None, None


# ------------------------------------------------
# Main Loader (Priority System)
# ------------------------------------------------

def load_model():
    """
    Load model using priority:
    1. JSON (manual override)
    2. Database (latest trained model)
    3. Fallback (default model)
    """

    # -----------------------------
    # 1. JSON Priority
    # -----------------------------
    model, model_id = _load_from_json()
    if model:
        print(f"[INFO] Loaded model from JSON: {model_id}")
        return model, model_id

    # -----------------------------
    # 2. Database Fallback
    # -----------------------------
    model, model_id = _load_from_db()
    if model:
        print(f"[INFO] Loaded model from DB: {model_id}")
        return model, model_id

    # -----------------------------
    # 3. Hardcoded Fallback
    # -----------------------------
    fallback_model = "loan_model_v1.pkl"

    print(f"[INFO] Loading fallback model: {fallback_model}")
    return _load_model_file(fallback_model)







































# import joblib
# import os
# import json
#
# # Base directory of this file
# BASE_DIR = os.path.dirname(__file__)
#
# # Metadata file path
# METADATA_PATH = os.path.abspath(
#     os.path.join(
#         BASE_DIR,
#         "../../ml/saved_models/model_metadata.json"
#     )
# )
#
#
# def load_model():
#     """
#     Load the machine learning model using metadata configuration.
#     This allows easy switching between model versions.
#     """
#
#     # Check metadata file
#     if not os.path.exists(METADATA_PATH):
#         raise FileNotFoundError(
#             f"Model metadata file not found: {METADATA_PATH}"
#         )
#
#     # Read metadata
#     with open(METADATA_PATH, "r") as f:
#         metadata = json.load(f)
#
#     model_file = metadata.get("current_model")
#
#     if not model_file:
#         raise ValueError("current_model not defined in metadata")
#
#     # Build model path
#     model_path = os.path.abspath(
#         os.path.join(
#             BASE_DIR,
#             f"../../ml/saved_models/{model_file}"
#         )
#     )
#
#     # Check model existence
#     if not os.path.exists(model_path):
#         raise FileNotFoundError(
#             f"Model file not found: {model_path}"
#         )
#
#     # Load model
#     model = joblib.load(model_path)
#
#     return model