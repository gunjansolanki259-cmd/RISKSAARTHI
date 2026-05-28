from app.utils.identity_utils import validate_pan, validate_aadhaar


def test_valid_pan():
    assert validate_pan("ABCDE1234F") is True


def test_invalid_pan():
    assert validate_pan("123") is False


def test_valid_aadhaar():
    assert validate_aadhaar("123456789012") is True


def test_invalid_aadhaar():
    assert validate_aadhaar("abcd") is False