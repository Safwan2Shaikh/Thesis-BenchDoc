# utils/logger.py

from datetime import datetime


def info(message):

    timestamp = datetime.now().strftime("%H:%M:%S")

    print(
        f"[{timestamp}] INFO: {message}"
    )


def error(message):

    timestamp = datetime.now().strftime("%H:%M:%S")

    print(
        f"[{timestamp}] ERROR: {message}"
    )