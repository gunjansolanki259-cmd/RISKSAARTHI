from unittest.mock import patch
from app.services.prediction_service import predict_loan_risk


@patch("app.services.prediction_service.prediction_logger")
def test_logging_called(mock_logger):

    from tests.test_prediction_service import DummyModel

    data = {
        "user_id": "1",
        "annual_income": 500000,
        "loan_amount": 200000,
        "loan_tenure": 60,
        "interest_rate": 7.5,
        "cibil_score": 750,
        "employment_type": "Salaried",
        "existing_loans": 1,
        "age": 30,
        "identity_hash": "abc",
        "identity_type": "PAN",
        "applicant_id": "xyz"
    }

    try:
        predict_loan_risk(data, DummyModel(), "test")
    except:
        pass

    assert mock_logger.info.called