import pandas as pd
from ml.data_generation.generate_synthetic_data import generate_data


def test_generate_data_rows():
    df = generate_data(50)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 50


def test_generate_data_columns():
    df = generate_data(10)

    expected_columns = [
        "age",
        "annual_income",
        "cibil_score",
        "loan_amount"
    ]

    for col in expected_columns:
        assert col in df.columns