from app.services.prediction_service import predict_loan_risk

# ------------------------------------------------
# TEST: Business Logic Tests
# ------------------------------------------------

class DummyModel:
    def predict(self, x): return [0]
    def predict_proba(self, x): return [[0.9, 0.1]]


def test_emi_calculation():
    input_data = {
        "user_id": "1",
        "annual_income": 500000,
        "loan_amount": 200000,
        "loan_tenure": 60,
        "interest_rate": 7.5,
        "cibil_score": 750,
        "employment_type": "Salaried",
        "existing_loans": 1,
        "age": 30
    }

    result = predict_loan_risk(input_data, DummyModel(), "test")

    assert result["emi"] > 0
    assert result["loan_decision"] in ["Approved", "Rejected"]