from fastapi import APIRouter, Request, HTTPException, status
from app.api.schemas import LoanRequest, LoanResponse
from app.services.prediction_service import predict_loan_risk
from app.services.analytics_service import get_analytics_data, get_prediction_history
from app.utils.logger import prediction_logger, error_logger
from app.services.contact_service import save_contact_message
from app.api.schemas import RegisterRequest, LoginRequest, AuthResponse
from app.services.user_service import register_user, login_user
from app.utils.identity_utils import hash_identity, generate_applicant_id, validate_identity
from typing import Optional

router = APIRouter()


# -----------------------------
# Loan Risk Prediction Endpoint
# -----------------------------
@router.post("/predict", response_model=LoanResponse)
def predict(request: LoanRequest, req: Request):

    try:
        model = req.app.state.model
        model_id = req.app.state.model_id

        if model is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Service temporarily unavailable"
            )

        # ----------------------------------------
        # Identity Handling
        # ----------------------------------------
        identity_number = request.identity_number
        identity_type = request.identity_type

        if not validate_identity(identity_type, identity_number):
            raise HTTPException(status_code=400, detail="Invalid identity format")

        identity_hash = hash_identity(identity_number)
        applicant_id = generate_applicant_id(identity_number)

        # ----------------------------------------
        # Prepare Input Data
        # ----------------------------------------
        input_data = request.model_dump(exclude_none=True)

        # Remove raw identity
        input_data.pop("identity_number", None)

        # Inject system-generated values
        input_data["applicant_id"] = applicant_id
        input_data["identity_hash"] = identity_hash
        input_data["identity_type"] = identity_type

        # ----------------------------------------
        # Prediction
        # ----------------------------------------
        prediction = predict_loan_risk(input_data, model, model_id)
        prediction["applicant_id"] = applicant_id

        prediction_logger.info(
            f"Prediction success | Applicant={applicant_id[:8]} | Model={model_id}"
        )

        return prediction

    # Preserve HTTPException
    except HTTPException as e:
        raise e

    except ValueError as e:
        error_logger.error(f"Validation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except KeyError as e:
        error_logger.error(f"Missing field: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Missing field: {str(e)}")

    except Exception as e:
        error_logger.error(f"Prediction Failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# -----------------------------
# Analytics Dashboard Endpoint
# -----------------------------
@router.get("/analytics")
def analytics(user_id: Optional[str] = None, mode: str = "user"):
    try:
        return get_analytics_data(user_id=user_id, mode=mode)

    except Exception as e:
        error_logger.error(f"Analytics Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# -----------------------------
# Prediction History Endpoint
# -----------------------------
@router.get("/history")
def history(user_id: Optional[str] = None, mode: str = "user", limit: int = 100):
    try:
        data = get_prediction_history(user_id=user_id, mode=mode)
        return data[:limit]

    except Exception as e:
        error_logger.error(f"History Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# -----------------------------
# MODEL INFORMATION
# -----------------------------
@router.get("/model-info")
def get_model_info(request: Request):
    try:
        model_id = request.app.state.model_id

        if not model_id:
            return {
                "model_name": "Unknown",
                "version": "N/A",
                "last_updated": "N/A"
            }

        return {
            "model_name": "Loan Risk Model",
            "version": model_id,
            "last_updated": "Loaded at runtime"
        }

    except Exception as e:
        error_logger.error(f"Model Info Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch model info")


# -----------------------------
# CONTACT US
# -----------------------------
@router.post("/contact")
def submit_contact(data: dict):

    if not data.get("name") or not data.get("email") or not data.get("message"):
        raise HTTPException(status_code=400, detail="All fields are required")

    return save_contact_message(data)


# -----------------------------
# REGISTER USER
# -----------------------------
@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest):
    return register_user(request.model_dump())


# -----------------------------
# LOGIN USER
# -----------------------------
@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest):
    return login_user(request.model_dump())
