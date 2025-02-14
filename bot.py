import logging
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import TelegramError
from config import TELEGRAM_TOKEN
from handlers import start_command, help_command, handle_message, button_callback, handle_document
from log_config import setup_logging

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

def init_application():
    """Initialize and configure the application"""
    try:
        # Create application instance
        application = Application.builder().token(TELEGRAM_TOKEN).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))

        # Add callback query handler for inline buttons
        application.add_handler(CallbackQueryHandler(button_callback))

        # Add document handler
        application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

        # Add message handler (should be last to catch all other text messages)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        return application
    except Exception as e:
        logging.error(f"Failed to initialize application: {str(e)}")
        raise

async def main():
    """Main function to run the bot"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting bot initialization...")
        logger.debug(f"Using token: {TELEGRAM_TOKEN[:4]}...{TELEGRAM_TOKEN[-4:]}")

        # Initialize application
        application = init_application()
        logger.info("Application initialized successfully")

        # Start the bot
        logger.info("Starting bot polling...")
        await application.run_polling(allowed_updates=Update.ALL_TYPES)
    except TelegramError as te:
        logger.error(f"Telegram API Error: {str(te)}")
        raise
    except Exception as e:
        logger.error(f"Critical error starting bot: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Bot crashed: {str(e)}")