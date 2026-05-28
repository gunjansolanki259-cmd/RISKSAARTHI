from pydantic import BaseModel, Field
from enum import Enum
from typing import List


# ------------------------------------------------
# ENUM
# ------------------------------------------------

class EmploymentType(str, Enum):
    salaried = "Salaried"
    self_employed = "Self-Employed"


class RiskLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class RiskBand(str, Enum):
    low = "Low Risk"
    medium = "Medium Risk"
    high = "High Risk"


# ------------------------------------------------
# INPUT SCHEMA
# ------------------------------------------------

class LoanRequest(BaseModel):
    applicant_id: str | None = None
    user_id: str | None = None

    identity_type: str
    identity_number: str

    age: int = Field(..., ge=21, le=60)
    annual_income: float = Field(..., gt=0)

    cibil_score: int = Field(..., ge=300, le=900)

    employment_type: EmploymentType

    loan_amount: float = Field(..., gt=0)
    loan_tenure: int = Field(..., ge=6, le=360)

    emi: float | None = Field(default=None, ge= 0)
    existing_loans: int = Field(..., ge=0, le=10)
    interest_rate: float = Field(..., gt=0, le=30)

    # ------------------------------------------------
    # Custom Validation
    # ------------------------------------------------

    # Swagger Example
    model_config = {
        "json_schema_extra": {
            "example": {
                "applicant_id": "USER123",
                "age": 30,
                "annual_income": 500000,
                "cibil_score": 750,
                "employment_type": "Salaried",
                "loan_amount": 200000,
                "loan_tenure": 60,
                "emi": 5000,
                "existing_loans": 1,
                "interest_rate": 10.5
            }
        }
    }


# ------------------------------------------------
# FEATURE IMPORTANCE SCHEMA
# ------------------------------------------------

class FeatureImportance(BaseModel):
    feature: str
    importance: float


# ------------------------------------------------
# OUTPUT SCHEMA
# ------------------------------------------------

class LoanResponse(BaseModel):
    prediction: int = Field(..., ge=0, le=1)

    probability: float = Field(
        ...,
        ge=0,
        le=100,
        description="Default probability in percentage"
    )

    risk_band: RiskBand
    risk_level: RiskLevel

    credit_score: int = Field(..., ge=300, le=900)

    explanation: str = Field(..., min_length=5)

    top_factors: List[FeatureImportance]

    applicant_id: str
    emi: float
    foir: float
    loan_decision: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "prediction": 0,
                "probability": 23.45,
                "risk_band": "Low Risk",
                "risk_level": "Low",
                "credit_score": 780,
                "explanation": "Applicant has strong income and high CIBIL score, indicating low risk.",
                "top_factors": [
                    {"feature": "cibil_score", "importance": 0.35},
                    {"feature": "annual_income", "importance": 0.25}
                ],
                "applicant_id": "RSK-8F3A1C2D"
            }
        }
    }

# ------------------------------------------------
# AUTH SCHEMAS
# ------------------------------------------------

class UserRole(str, Enum):
    loan_officer = "Loan Officer"
    risk_analyst = "Risk Analyst"
    user = "System User"



class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=6)
    role: UserRole   # ✅ ADD THIS

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Devansh",
                "email": "devansh@email.com",
                "password": "secure123",
                "role": "User"
            }
        }
    }


class LoginRequest(BaseModel):
    email: str
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "devansh@email.com",
                "password": "secure123"
            }
        }
    }


class AuthResponse(BaseModel):
    status: str
    message: str = None
    user_id: str = None
    name: str = None
    email: str = None