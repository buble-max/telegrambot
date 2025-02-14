import os

# Telegram Bot Token - Should be set as an environment variable
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

if not TELEGRAM_TOKEN:
    raise ValueError(
        "No Telegram token found! Please set the TELEGRAM_TOKEN environment variable."
    )

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
