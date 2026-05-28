from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.models.model_loader import load_model

client = TestClient(app)


# ------------------------------------------------
# Setup Model
# ------------------------------------------------
def setup_module():
    model, model_id = load_model()
    app.state.model = model
    app.state.model_id = model_id


# ------------------------------------------------
# TEST: Model Info
# ------------------------------------------------
def test_model_info():
    response = client.get("/api/model-info")

    assert response.status_code == 200
    data = response.json()

    assert "model_name" in data
    assert "version" in data


# ------------------------------------------------
# TEST: Predict Success
# ------------------------------------------------
@patch("app.services.prediction_service.save_application")
@patch("app.services.prediction_service.save_prediction_result")
def test_predict_success(mock_save_pred, mock_save_app):

    mock_save_app.return_value = 123
    mock_save_pred.return_value = None

    payload = {
        "user_id": "1",
        "identity_type": "PAN",
        "identity_number": "ABCDE1234F",
        "age": 30,
        "annual_income": 500000,
        "cibil_score": 750,
        "employment_type": "Salaried",
        "loan_amount": 200000,
        "loan_tenure": 60,
        "existing_loans": 1,
        "interest_rate": 7.5
    }

    response = client.post("/api/predict", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert "probability" in data
    assert "risk_level" in data
    assert "credit_score" in data
    assert "loan_decision" in data


# ------------------------------------------------
# TEST: Invalid Payload
# ------------------------------------------------
def test_predict_invalid_payload():
    payload = {
        "user_id": 1,
        "identity_type": "PAN",
        "identity_number": "INVALID",
        "age": -1,
    }

    response = client.post("/api/predict", json=payload)

    assert response.status_code in [400, 422]


# ------------------------------------------------
# TEST: Boundary Values (FIXED)
# ------------------------------------------------
@patch("app.services.prediction_service.save_application")
@patch("app.services.prediction_service.save_prediction_result")
def test_predict_boundary_values(mock_save_pred, mock_save_app):

    mock_save_app.return_value = 123
    mock_save_pred.return_value = None

    payload = {
        "user_id": "1",
        "identity_type": "PAN",
        "identity_number": "ABCDE1234F",
        "age": 21,
        "annual_income": 1,
        "cibil_score": 300,
        "employment_type": "Salaried",
        "loan_amount": 1,
        "loan_tenure": 6,
        "existing_loans": 0,
        "interest_rate": 0.1
    }

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200


# ------------------------------------------------
# TEST: Invalid Identity Format
# ------------------------------------------------
def test_invalid_identity_format():
    payload = {
        "user_id": "1",
        "identity_type": "PAN",
        "identity_number": "WRONG123",
        "age": 30,
        "annual_income": 500000,
        "cibil_score": 750,
        "employment_type": "Salaried",
        "loan_amount": 200000,
        "loan_tenure": 60,
        "existing_loans": 1,
        "interest_rate": 7.5
    }

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400


# ------------------------------------------------
# TEST: Security
# ------------------------------------------------
@patch("app.services.prediction_service.save_application")
@patch("app.services.prediction_service.save_prediction_result")
def test_identity_not_exposed(mock_save_pred, mock_save_app):

    mock_save_app.return_value = 123
    mock_save_pred.return_value = None

    payload = {
        "user_id": "1",
        "identity_type": "PAN",
        "identity_number": "ABCDE1234F",
        "age": 30,
        "annual_income": 500000,
        "cibil_score": 750,
        "employment_type": "Salaried",
        "loan_amount": 200000,
        "loan_tenure": 60,
        "existing_loans": 1,
        "interest_rate": 7.5
    }

    response = client.post("/api/predict", json=payload)
    data = response.json()

    assert "identity_number" not in data


# ------------------------------------------------
# TEST: DB Failure
# ------------------------------------------------
@patch("app.services.prediction_service.save_application")
def test_db_failure(mock_save):

    mock_save.side_effect = Exception("DB error")

    payload = {
        "user_id": "1",
        "identity_type": "PAN",
        "identity_number": "ABCDE1234F",
        "age": 30,
        "annual_income": 500000,
        "cibil_score": 750,
        "employment_type": "Salaried",
        "loan_amount": 200000,
        "loan_tenure": 60,
        "existing_loans": 1,
        "interest_rate": 7.5
    }

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200


# ------------------------------------------------
# TEST: Deterministic Prediction
# ------------------------------------------------
@patch("app.services.prediction_service.save_application")
@patch("app.services.prediction_service.save_prediction_result")
def test_prediction_consistency(mock_save_pred, mock_save_app):

    mock_save_app.return_value = 123
    mock_save_pred.return_value = None

    payload = {
        "user_id": "1",
        "identity_type": "PAN",
        "identity_number": "ABCDE1234F",
        "age": 30,
        "annual_income": 500000,
        "cibil_score": 750,
        "employment_type": "Salaried",
        "loan_amount": 200000,
        "loan_tenure": 60,
        "existing_loans": 1,
        "interest_rate": 7.5
    }

    r1 = client.post("/api/predict", json=payload).json()
    r2 = client.post("/api/predict", json=payload).json()

    assert r1["prediction"] == r2["prediction"]


# ------------------------------------------------
# TEST: Preprocessing
# ------------------------------------------------
def test_preprocess_handles_missing_optional_api():
    from app.models.preprocess import preprocess_input

    data = {
        "age": 30,
        "annual_income": 500000,
        "cibil_score": 750,
        "loan_amount": 200000,
        "loan_tenure": 60,
        "emi": 4000,
        "existing_loans": 1,
        "employment_type": "Salaried"
    }

    processed = preprocess_input(data)

    assert processed.shape[0] == 1


@patch("app.services.prediction_service.save_application")
def test_db_called(mock_save):

    mock_save.return_value = 123

    payload = {
  "user_id": "USR001",
  "identity_type": "PAN",
  "identity_number": "ABCDE1234F",
  "age": 32,
  "annual_income": 1200000,
  "cibil_score": 780,
  "employment_type": "Salaried",
  "loan_amount": 200000,
  "loan_tenure": 24,
  "existing_loans": 0,
  "interest_rate": 10.5
}

    client.post("/api/predict", json=payload)

    assert mock_save.called
