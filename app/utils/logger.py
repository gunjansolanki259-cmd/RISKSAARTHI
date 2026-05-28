import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def setup_logger(name, log_file, level=logging.INFO):

    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, log_file),
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Different loggers
app_logger = setup_logger("app", "app.log")
prediction_logger = setup_logger("prediction", "prediction.log")
user_activity_logger = setup_logger("user_activity", "user_activity.log")
error_logger = setup_logger("error", "error.log", level=logging.ERROR)
auth_logger = setup_logger("auth", "auth.log")
registration_logger = setup_logger("registration", "registration.log")