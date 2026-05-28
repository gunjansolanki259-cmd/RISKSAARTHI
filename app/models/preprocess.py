import pandas as pd


def preprocess_input(data: dict):
    df = pd.DataFrame([data])

    # ------------------------------------------------
    # Required input validation
    # ------------------------------------------------
    required_columns = [
        "age",
        "annual_income",
        "cibil_score",
        "loan_amount",
        "loan_tenure",
        "emi",
        "existing_loans",
        "employment_type"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # ------------------------------------------------
    # Remove non-model columns
    # ------------------------------------------------
    drop_cols = ["applicant_id", "application_id", "user_id"]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns])

    # ------------------------------------------------
    # Encode employment_type
    # ------------------------------------------------
    employment_map = {
        "Salaried": 0,
        "Self-Employed": 1
    }

    if df["employment_type"].iloc[0] not in employment_map:
        raise ValueError("Invalid employment_type")

    df["employment_type"] = df["employment_type"].map(employment_map)

    # ------------------------------------------------
    # Ensure correct data types
    # ------------------------------------------------
    numeric_cols = [
        "age", "annual_income", "cibil_score",
        "loan_amount", "loan_tenure", "emi", "existing_loans"
    ]

    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    if df[numeric_cols].isnull().any().any():
        raise ValueError("Invalid numeric input detected")

    # ------------------------------------------------
    # EMI CONSISTENCY FIX
    # ------------------------------------------------
    # IMPORTANT:
    # Model was trained using provided EMI → do NOT recalculate
    # Just validate logical consistency

    loan_amount = df.loc[0, "loan_amount"]
    tenure = df.loc[0, "loan_tenure"]
    emi = df.loc[0, "emi"]

    if tenure <= 0:
        raise ValueError("Loan tenure must be greater than 0")

    if emi <= 0:
        raise ValueError("EMI must be greater than 0")

    # ------------------------------------------------
    # Final column order (important for model)
    # ------------------------------------------------
    df = df[[
        "age",
        "annual_income",
        "cibil_score",
        "employment_type",
        "loan_amount",
        "loan_tenure",
        "emi",
        "existing_loans"
    ]]

    return df