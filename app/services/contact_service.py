from app.services.db_service import get_connection
from app.utils.logger import user_activity_logger, error_logger


def save_contact_message(data):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        user_id = str(data.get("user_id"))

        query = """
            INSERT INTO contact_messages (user_id, name, email, message)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            user_id,
            data.get("name"),
            data.get("email"),
            data.get("message")
        )

        cursor.execute(query, values)
        conn.commit()

        user_activity_logger.info(f"[USER {user_id}] Submitted Contact Form")

        return {
            "status": "success",
            "message": "Message saved successfully"
        }

    except Exception as e:
        conn.rollback()
        error_logger.error(f"Contact Save Error: {str(e)}")

        return {
            "status": "error",
            "message": "Failed to save message"
        }

    finally:
        cursor.close()
        conn.close()