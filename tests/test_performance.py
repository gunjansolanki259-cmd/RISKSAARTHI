import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ------------------------------------------------
# TEST: Performance Test
# ------------------------------------------------

def test_prediction_speed():
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

    start = time.time()
    response = client.post("/api/predict", json=payload)
    end = time.time()

    assert response.status_code == 200
    assert (end - start) < 2