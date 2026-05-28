import hashlib
from app.config import settings
import re


def hash_identity(identity_number: str) -> str:
    """
    Hash Aadhaar/PAN (for storage)
    """
    return hashlib.sha256(identity_number.encode()).hexdigest()


def generate_applicant_id(identity_number: str) -> str:
    """
    Generate consistent applicant ID using salt
    """
    raw = identity_number + settings.IDENTITY_SALT
    return hashlib.sha256(raw.encode()).hexdigest()



def validate_pan(pan: str) -> bool:
    """
    Validates PAN format: ABCDE1234F
    """
    if not isinstance(pan, str):
        return False
    pan = pan.upper().strip()
    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan))


def validate_aadhaar(aadhaar: str) -> bool:
    """
    Validates Aadhaar: 12 digit numeric
    """
    if not isinstance(aadhaar, str):
        return False
    aadhaar = aadhaar.strip()
    return bool(re.fullmatch(r"\d{12}", aadhaar))


def validate_identity(identity_type: str, identity_number: str) -> bool:
    """
    Generic validator for identity
    """
    if identity_type == "PAN":
        return validate_pan(identity_number)
    elif identity_type == "Aadhaar":
        return validate_aadhaar(identity_number)
    return False