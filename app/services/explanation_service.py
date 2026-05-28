def generate_explanation(data: dict) -> list:
    explanations = []

    cibil = data.get("cibil_score", 0)
    income = data.get("annual_income", 0)
    loan = data.get("loan_amount", 0)
    age = data.get("age", 0)
    emi = data.get("emi", 0)
    existing = data.get("existing_loans", 0)

    # ===============================
    # Credit Score Analysis
    # ===============================
    if cibil < 600:
        explanations.append("Low CIBIL score indicates higher default risk")
    elif cibil < 700:
        explanations.append("Moderate CIBIL score — credit profile is average")
    else:
        explanations.append("Strong CIBIL score reflects good creditworthiness")

    # ===============================
    # Income Strength
    # ===============================
    if income < 300000:
        explanations.append("Low annual income reduces repayment capacity")
    elif income > 1000000:
        explanations.append("High income improves repayment capability")

    # ===============================
    # Loan Burden
    # ===============================
    if income > 0:
        loan_ratio = loan / income

        if loan_ratio > 0.6:
            explanations.append("Loan amount is very high compared to income")
        elif loan_ratio > 0.4:
            explanations.append("Loan amount is moderately high relative to income")

    # ===============================
    # EMI / FOIR Logic
    # ===============================
    if income > 0:
        monthly_income = income / 12

        if emi > 0:
            foir = (emi / monthly_income) * 100

            if foir > 60:
                explanations.append("Very high FOIR indicates financial stress")
            elif foir > 40:
                explanations.append("Moderate FOIR suggests manageable debt")
            else:
                explanations.append("Low FOIR indicates healthy financial position")
        else:
            explanations.append("No existing EMI obligations")

    # ===============================
    # Existing Loans
    # ===============================
    if existing >= 3:
        explanations.append("Multiple active loans increase repayment risk")
    elif existing == 0:
        explanations.append("No active loans — lower debt burden")

    # ===============================
    # Age Factor
    # ===============================
    if age < 23:
        explanations.append("Limited credit history due to young age")
    elif age > 55:
        explanations.append("Higher age may impact long-term repayment capacity")

    # ===============================
    # Fallback
    # ===============================
    if not explanations:
        explanations.append("Applicant profile appears financially stable")

    return explanations
