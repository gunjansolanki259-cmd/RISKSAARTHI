from app.models.preprocess import preprocess_input
from app.services.explanation_service import generate_explanation
from app.services.db_service import save_application, save_prediction_result
from app.utils.logger import prediction_logger, error_logger
from app.models.feature_importance import get_feature_importance


def predict_loan_risk(input_data: dict, model, model_id):

    try:
        # ------------------------------------------------
        # 1. CALCULATE EMI FIRST
        # ------------------------------------------------
        try:
            loan_amount = input_data["loan_amount"]
            annual_income = input_data["annual_income"]
            tenure = input_data["loan_tenure"]
            interest_rate = input_data["interest_rate"]
        except Exception:
            raise ValueError("Invalid numeric input detected in EMI calculation")

        if loan_amount <= 0 or tenure <= 0:
            raise ValueError("Loan amount and tenure must be > 0")

        r = interest_rate / (12 * 100)
        n = tenure

        if r == 0:
            emi = loan_amount / n
        else:
            emi = (loan_amount * r * (1 + r) ** n) / ((1 + r) ** n - 1)

        emi = round(emi, 2)

        print(f"EMI DEBUG → Loan:{loan_amount}, Rate:{interest_rate}, Tenure:{tenure}, EMI:{emi}")

        # Inject EMI
        input_data["emi"] = emi

        # ------------------------------------------------
        # 2. Preprocess Input
        # ------------------------------------------------
        processed = preprocess_input(input_data)

        # ------------------------------------------------
        # 3. Model Prediction
        # ------------------------------------------------
        prediction = model.predict(processed)[0]
        probability = model.predict_proba(processed)[0][1]
        risk_percentage = round(probability * 100, 2)

        feature_importance = get_feature_importance(
            model,
            processed.columns.tolist()
        )

        # ------------------------------------------------
        # 4. Risk Level + Band
        # ------------------------------------------------
        if probability < 0.3:
            risk_level = "Low"
            risk_band = "Low Risk"
        elif probability < 0.6:
            risk_level = "Medium"
            risk_band = "Medium Risk"
        else:
            risk_level = "High"
            risk_band = "High Risk"

        # ------------------------------------------------
        # 5. Credit Score
        # ------------------------------------------------
        credit_score = int(300 + (1 - probability) * 600)

        # ------------------------------------------------
        # 6. Financial Calculations
        # ------------------------------------------------
        monthly_income = max(annual_income / 12, 1)
        foir = round((emi / monthly_income) * 100, 2)

        if probability < 0.5 and foir < 40:
            loan_decision = "Approved"
        else:
            loan_decision = "Rejected"

        # ------------------------------------------------
        # 7. Explanation
        # ------------------------------------------------
        explanation = generate_explanation(input_data)
        if isinstance(explanation, list):
            explanation = " | ".join(explanation)

        # ------------------------------------------------
        # 8. SAFE DB SAVE
        # ------------------------------------------------
        application_id = None

        try:
            if input_data.get("user_id") and input_data.get("identity_hash"):
                application_id = save_application(input_data)

                save_prediction_result(application_id, model_id, {
                    "probability": float(probability),
                    "risk_level": risk_band,
                    "credit_score": credit_score,
                    "loan_decision": loan_decision,
                    "foir": foir,
                    "emi": emi,
                    "explanation": explanation
                })

        except Exception as db_error:
            # ❗ DO NOT FAIL PREDICTION
            error_logger.error(f"DB Save Skipped: {str(db_error)}")

        # ------------------------------------------------
        # 9. Logging
        # ------------------------------------------------
        prediction_logger.info(
            f"Application {application_id} | "
            f"Model={model_id} | "
            f"Risk={risk_level} | Prob={probability:.4f} | Decision={loan_decision}"
        )

        # ------------------------------------------------
        # 10. RESPONSE
        # ------------------------------------------------
        return {
            "prediction": int(prediction),
            "probability": risk_percentage,
            "risk_band": risk_band,
            "risk_level": risk_level,
            "credit_score": credit_score,
            "explanation": explanation,
            "top_factors": feature_importance[:5],
            "emi": emi,
            "foir": foir,
            "loan_decision": loan_decision
        }

    except Exception as e:
        error_logger.error(f"Prediction Service Error: {str(e)}")
        raise Exception("Prediction failed")
