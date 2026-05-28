from app.services.explanation_service import generate_explanation


def test_generate_explanation_returns_string():
    data = {
        "cibil_score": 750,
        "annual_income": 500000,
        "loan_amount": 200000,
        "existing_loans": 1,
        "emi": 4000
    }

    result = generate_explanation(data)

    assert isinstance(result, (str, list))


def test_generate_explanation_not_empty():
    data = {
        "cibil_score": 300,
        "annual_income": 100000,
        "loan_amount": 500000,
        "existing_loans": 5,
        "emi": 20000
    }

    result = generate_explanation(data)

    assert result is not None
    assert len(result) > 0