import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def send_error_message(
    update: Optional[Update],
    context: ContextTypes.DEFAULT_TYPE,
    error_message: str = "An error occurred. Please try again later."
):
    """Utility function to send error messages to users"""
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                f"❌ {error_message}"
            )
    except Exception as e:
        logger.error(f"Failed to send error message: {str(e)}")

def log_user_action(update: Update, action: str):
    """Utility function to log user actions"""
    user = update.effective_user
    logger.info(
        f"User {user.id} ({user.username or 'No username'}) performed action: {action}"
    )