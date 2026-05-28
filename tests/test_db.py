from app.services.db_service import get_connection
from unittest.mock import patch, MagicMock
from app.services.db_service import save_application


def test_db_connection():
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute("SELECT 1")

    result = cursor.fetchone()

    assert result[0] == 1

    conn.close()



@patch("app.services.db_service.get_connection")
def test_save_application_success(mock_conn):

    mock_cursor = MagicMock()
    mock_conn.return_value.cursor.return_value = mock_cursor

    # Mock fraud check count
    mock_cursor.fetchone.return_value = [0]

    data = {
        "applicant_id": "abc123",
        "user_id": "1",
        "identity_hash": "hash123",
        "identity_type": "PAN",
        "age": 30,
        "annual_income": 500000,
        "cibil_score": 750,
        "employment_type": "Salaried",
        "loan_amount": 200000,
        "loan_tenure": 60,
        "interest_rate": 7.5,
        "emi": 4000
    }

    result = save_application(data)

    assert result is not None
    assert mock_cursor.execute.called