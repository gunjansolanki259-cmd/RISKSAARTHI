import uuid
import bcrypt

from app.services.db_service import get_connection
from app.utils.logger import error_logger, auth_logger, registration_logger


# ------------------------------------------------
# HASH PASSWORD
# ------------------------------------------------
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


# ------------------------------------------------
# VERIFY PASSWORD
# ------------------------------------------------
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ------------------------------------------------
# REGISTER USER
# ------------------------------------------------
def register_user(data: dict):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        user_id = str(uuid.uuid4())

        name = data.get("name")
        email = data.get("email")
        role = data.get("role")
        password = data.get("password")

        hashed_password = hash_password(password)

        query = """
        INSERT INTO users (user_id, name, email, role, password)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            user_id,
            name,
            email,
            role,
            hashed_password
        )

        cursor.execute(query, values)
        conn.commit()

        # Success log
        registration_logger.info(
            f"[USER {user_id}] Registered successfully | Email: {email} | Role: {role}"
        )

        return {
            "status": "success",
            "user_id": user_id,
            "message": "User registered successfully"
        }

    except Exception as e:
        conn.rollback()

        # Failure log
        registration_logger.error(
            f"[REGISTRATION FAILED] Email: {data.get('email')} | Error: {str(e)}"
        )

        error_logger.error(f"Register Error: {str(e)}")

        return {
            "status": "error",
            "message": "Registration failed (email may already exist)"
        }

    finally:
        cursor.close()
        conn.close()


# ------------------------------------------------
# LOGIN USER
# ------------------------------------------------
def login_user(data: dict):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        email = data.get("email")
        password = data.get("password")

        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))

        user = cursor.fetchone()

        # User not found
        if not user:
            auth_logger.warning(f"[LOGIN FAILED] Email: {email} | Reason: User not found")
            return {
                "status": "error",
                "message": "Invalid email or password"
            }

        # Wrong password
        if not verify_password(password, user["password"]):
            auth_logger.warning(f"[LOGIN FAILED] Email: {email} | Reason: Wrong password")
            return {
                "status": "error",
                "message": "Invalid email or password"
            }

        # Success
        auth_logger.info(f"[USER {user['user_id']}] Login successful")

        return {
            "status": "success",
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"]
        }

    except Exception as e:
        error_logger.error(f"Login Error: {str(e)}")

        return {
            "status": "error",
            "message": "Login failed"
        }

    finally:
        cursor.close()
        conn.close()