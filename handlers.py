import logging
import os
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from file_converter import FileConverter
from utils import send_error_message, log_user_action

logger = logging.getLogger(__name__)
file_converter = FileConverter()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    log_user_action(update, "started the bot")

    keyboard = [
        [
            InlineKeyboardButton("Word to PDF", callback_data='word_to_pdf'),
            InlineKeyboardButton("PDF to Word", callback_data='pdf_to_word')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = (
        "👋 Welcome to the File Converter Bot!\n\n"
        "I can help you convert files between Word and PDF formats.\n"
        "Please select one of the options below:\n"
    )

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    log_user_action(update, "requested help")

    help_message = (
        "🔍 Help Information\n\n"
        "Available commands:\n"
        "/start - Start the bot and show conversion options\n"
        "/help - Show this help message\n\n"
        "To convert a file:\n"
        "1. Click /start\n"
        "2. Choose the conversion type\n"
        "3. Send your file when prompted\n\n"
        "Supported formats:\n"
        "• Word (.doc, .docx)\n"
        "• PDF (.pdf)"
    )

    await update.message.reply_text(help_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    log_user_action(update, f"sent message: {update.message.text}")

    response = (
        "Please use /start to see the available file conversion options, "
        "or /help for more information about how to use this bot."
    )

    await update.message.reply_text(response)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    if query.data == 'word_to_pdf':
        await query.message.reply_text(
            "📤 Please send me the Word document (.doc or .docx) you want to convert to PDF."
        )
        context.user_data['conversion_type'] = 'word_to_pdf'
    elif query.data == 'pdf_to_word':
        await query.message.reply_text(
            "📤 Please send me the PDF file you want to convert to Word format."
        )
        context.user_data['conversion_type'] = 'pdf_to_word'

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document messages"""
    if not update.message.document:
        await update.message.reply_text("❌ Please send a document file.")
        return

    conversion_type = context.user_data.get('conversion_type')
    if not conversion_type:
        await update.message.reply_text(
            "❌ Please use /start first to select a conversion type."
        )
        return

    file_name = update.message.document.file_name
    file_size = update.message.document.file_size
    logger.info(f"Received file: {file_name} (size: {file_size} bytes) for conversion type: {conversion_type}")

    # Check if file has a name
    if not file_name:
        await update.message.reply_text(
            "❌ The file must have a valid name with the correct extension (.doc, .docx, or .pdf)"
        )
        return

    # Validate file extension with more detailed error messages
    if conversion_type == 'word_to_pdf':
        if not file_name.lower().endswith(('.doc', '.docx')):
            await update.message.reply_text(
                "❌ For Word to PDF conversion, please send a valid Word document.\n"
                "Supported formats: .doc or .docx"
            )
            return
    elif conversion_type == 'pdf_to_word':
        if not file_name.lower().endswith('.pdf'):
            await update.message.reply_text(
                "❌ For PDF to Word conversion, please send a valid PDF file.\n"
                "Supported format: .pdf"
            )
            return

    # Validate file size (max 20MB)
    max_size = 20 * 1024 * 1024  # 20MB in bytes
    if file_size > max_size:
        await update.message.reply_text(
            "❌ File is too large. Maximum file size is 20MB."
        )
        return

    download_path = None
    output_path = None

    try:
        # Create temp directory if it doesn't exist
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        logger.info(f"Temp directory status - exists: {temp_dir.exists()}, is_dir: {temp_dir.is_dir()}")

        # Download the file
        file = await context.bot.get_file(update.message.document.file_id)
        download_path = temp_dir / file_name
        logger.info(f"Downloading file to {download_path}")
        await file.download_to_drive(str(download_path))

        # Verify downloaded file
        if not os.path.exists(str(download_path)):
            raise FileNotFoundError(f"Downloaded file not found at {download_path}")

        downloaded_size = os.path.getsize(str(download_path))
        logger.info(f"File downloaded successfully. Size: {downloaded_size} bytes")

        await update.message.reply_text("⚙️ Converting your file... Please wait.")
        logger.info("Starting file conversion process...")

        # Convert the file
        if conversion_type == 'word_to_pdf':
            output_path = file_converter.word_to_pdf(str(download_path))
            output_name = Path(output_path).name
            output_size = os.path.getsize(output_path)
            logger.info(f"PDF conversion completed. Output size: {output_size} bytes")

            # Send the converted PDF
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=open(output_path, 'rb'),
                filename=output_name,
                caption="✅ Here's your converted PDF file!"
            )
        else:  # pdf_to_word
            output_path = file_converter.pdf_to_word(str(download_path))
            output_name = Path(output_path).name
            output_size = os.path.getsize(output_path)
            logger.info(f"Word conversion completed. Output size: {output_size} bytes")

            # Send the converted Word document
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=open(output_path, 'rb'),
                filename=output_name,
                caption="✅ Here's your converted Word document!"
            )

    except FileNotFoundError as e:
        logger.error(f"File not found error: {str(e)}")
        await update.message.reply_text(
            "❌ Error: The file could not be processed. Please try uploading again."
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}\n"
            "Please make sure you're sending the correct file type for the selected conversion."
        )
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "❌ Sorry, there was an error processing your file. Please try again."
        )
    finally:
        # Cleanup temporary files
        if download_path and os.path.exists(str(download_path)):
            file_converter.cleanup_temp_files(str(download_path))
        if output_path and os.path.exists(output_path):
            file_converter.cleanup_temp_files(output_path)