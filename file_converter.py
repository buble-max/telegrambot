import logging
import os
from pathlib import Path
from docx import Document
from fpdf import FPDF
from pdf2docx import Converter

logger = logging.getLogger(__name__)

class FileConverter:
    def __init__(self):
        # Use absolute path for temp directory and ensure it exists with proper permissions
        self.temp_dir = Path(os.getcwd()) / "temp"
        try:
            self.temp_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
            logger.info(f"Temporary directory created/verified at {self.temp_dir}")
        except Exception as e:
            logger.error(f"Failed to create temp directory: {str(e)}")
            raise

    def word_to_pdf(self, word_file_path: str) -> str:
        """Convert Word document to PDF"""
        try:
            logger.info(f"Starting Word to PDF conversion for {word_file_path}")

            # Verify file extension
            file_ext = Path(word_file_path).suffix.lower()
            if file_ext not in ['.doc', '.docx']:
                raise ValueError(f"Invalid file extension: {file_ext}. Expected .doc or .docx")

            # Verify input file exists and is readable
            if not os.path.exists(word_file_path):
                raise FileNotFoundError(f"Input file not found: {word_file_path}")

            # Log file size
            file_size = os.path.getsize(word_file_path)
            logger.info(f"Input file size: {file_size} bytes")

            # Create PDF with proper configuration
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Read Word document
            logger.debug("Opening Word document...")
            doc = Document(word_file_path)
            logger.debug("Word document opened successfully")

            # Set font (using a font that's guaranteed to be available)
            pdf.set_font("Helvetica", size=12)

            # Process paragraphs with better text handling
            logger.debug("Processing paragraphs...")
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():  # Skip empty paragraphs
                    # Handle text encoding more robustly
                    cleaned_text = "".join(char for char in paragraph.text if ord(char) < 128)
                    pdf.multi_cell(w=0, h=10, txt=cleaned_text)
            logger.debug("Paragraphs processed successfully")

            # Save PDF with absolute path
            output_path = str(self.temp_dir / f"{Path(word_file_path).stem}.pdf")
            logger.debug(f"Saving PDF to {output_path}")
            pdf.output(output_path)

            if not os.path.exists(output_path):
                raise FileNotFoundError(f"Output file not found at {output_path}")

            logger.info(f"Successfully converted Word file to PDF: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error converting Word to PDF: {str(e)}", exc_info=True)
            if os.path.exists(word_file_path):
                logger.error(f"Input file size: {os.path.getsize(word_file_path)} bytes")
            raise

    def pdf_to_word(self, pdf_file_path: str) -> str:
        """Convert PDF to Word document"""
        try:
            logger.info(f"Starting PDF to Word conversion for {pdf_file_path}")

            # Verify file extension
            file_ext = Path(pdf_file_path).suffix.lower()
            if file_ext != '.pdf':
                raise ValueError(f"Invalid file extension: {file_ext}. Expected .pdf")

            # Verify input file exists and is readable
            if not os.path.exists(pdf_file_path):
                raise FileNotFoundError(f"Input file not found: {pdf_file_path}")

            # Log file size
            file_size = os.path.getsize(pdf_file_path)
            logger.info(f"Input file size: {file_size} bytes")

            # Create output path with absolute path
            output_path = str(self.temp_dir / f"{Path(pdf_file_path).stem}.docx")
            logger.debug(f"Output path set to {output_path}")

            # Convert PDF to Word with proper error handling
            logger.debug("Initializing PDF converter...")
            cv = Converter(pdf_file_path)
            logger.debug("Starting conversion process...")
            cv.convert(output_path, start=0, end=None)
            cv.close()
            logger.debug("Conversion completed")

            if not os.path.exists(output_path):
                raise FileNotFoundError(f"Conversion completed but output file not found at {output_path}")

            logger.info(f"Successfully converted PDF to Word: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error converting PDF to Word: {str(e)}", exc_info=True)
            if os.path.exists(pdf_file_path):
                logger.error(f"Input file size: {os.path.getsize(pdf_file_path)} bytes")
            raise

    def cleanup_temp_files(self, file_path: str):
        """Remove temporary files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {str(e)}")