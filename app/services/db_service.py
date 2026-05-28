from mysql.connector import pooling
from app.config import settings
from app.utils.logger import error_logger
import uuid

# ------------------------------------------------
# Connection Pool
# ------------------------------------------------

connection_pool = pooling.MySQLConnectionPool(
    pool_name="risksaarthi_pool",
    pool_size=5,
    host=settings.DB_HOST,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_NAME
)


def get_connection():
    return connection_pool.get_connection()


# ------------------------------------------------
# Save Loan Application
# ------------------------------------------------

def save_application(data: dict):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        application_id = str(uuid.uuid4())

        identity_hash = data.get("identity_hash")

        # 🔒 OPTIONAL FRAUD CHECK (SAFE)
        if identity_hash:
            cursor.execute("""
            SELECT COUNT(*) FROM loan_applications
            WHERE identity_hash = %s
            """, (identity_hash,))

            count = cursor.fetchone()[0]

            if count > 15:
                raise Exception("Too many attempts from same identity")

        # INSERT QUERY
        query = """
        INSERT INTO loan_applications
        (application_id, applicant_id, user_id,
         identity_hash, identity_type,
         age, annual_income, cibil_score,
         employment_type, loan_amount, emi, loan_tenure, interest_rate)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            application_id,
            data.get("applicant_id"),
            data.get("user_id"),

            identity_hash,
            data.get("identity_type"),

            data.get("age"),
            data.get("annual_income"),
            data.get("cibil_score"),
            data.get("employment_type"),
            data.get("loan_amount"),
            data.get("emi", 0),
            data.get("loan_tenure"),
            data.get("interest_rate")
        )

        cursor.execute(query, values)
        conn.commit()

        return application_id

    except Exception as e:
        error_logger.error(f"DB Save Application Failed: {str(e)}", exc_info=True)
        raise Exception("Failed to save loan application")

    finally:
        cursor.close()
        conn.close()


# ------------------------------------------------
# Save Prediction Result
# ------------------------------------------------

def save_prediction_result(application_id: str, model_id: str, result: dict):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        prediction_id = str(uuid.uuid4())

        query = """
        INSERT INTO prediction_results
        (prediction_id, application_id, model_id,
         default_probability, risk_category,
         credit_score, loan_decision,
         foir, emi, explanation_text)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            prediction_id,
            application_id,
            model_id,
            result.get("probability"),
            result.get("risk_level"),
            result.get("credit_score"),
            result.get("loan_decision"),
            result.get("foir"),
            result.get("emi"),
            result.get("explanation", "")
        )

        cursor.execute(query, values)
        conn.commit()

    except Exception as e:
        error_logger.error(f"DB Save Prediction Failed: {str(e)}", exc_info=True)
        raise Exception("Failed to save prediction result")

    finally:
        cursor.close()
        conn.close()


# ------------------------------------------------
# Fetch Prediction History
# ------------------------------------------------

def get_prediction_history():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
        SELECT 
            pr.prediction_id,
            pr.application_id,
            la.applicant_id,
            la.user_id,
            la.identity_type,
            pr.model_id,
            pr.default_probability,
            pr.risk_category,
            pr.credit_score,
            pr.loan_decision,
            pr.foir,
            pr.emi,
            pr.explanation_text,
            pr.prediction_time
        FROM prediction_results pr
        JOIN loan_applications la
        ON la.application_id = pr.application_id 
        ORDER BY pr.prediction_time DESC
        """

        cursor.execute(query)
        return cursor.fetchall()

    except Exception as e:
        error_logger.error(f"DB Fetch History Failed: {str(e)}", exc_info=True)
        raise Exception("Failed to fetch prediction history")

    finally:
        cursor.close()
        conn.close()
