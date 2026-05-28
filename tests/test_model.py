import numpy as np
from app.models.model_loader import load_model
from app.models.preprocess import preprocess_input


def test_model_load():
    model, model_id = load_model()
    assert model is not None


def test_preprocess_output_shape():
    sample_input = {
        "age": 30,
        "annual_income": 500000,
        "cibil_score": 750,
        "employment_type": "Salaried",
        "loan_amount": 200000,
        "loan_tenure": 60,
        "existing_loans": 1,
        "interest_rate": 7.5,
        "emi": 4000
    }

    processed = preprocess_input(sample_input)
    assert processed is not None


def test_model_prediction():
    model, model_id = load_model()

    sample = np.array([[30, 500000, 750, 1, 200000, 60, 1, 7.5]])

    pred = model.predict(sample)

    assert pred is not None


def test_preprocess_handles_missing_optional():
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