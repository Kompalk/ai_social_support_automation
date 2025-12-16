"""Text extraction from various document formats."""
import pdfplumber
import PyPDF2
from docx import Document
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TextExtractor:
    """Extract text from PDF and DOCX files."""
    
    def extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            # Try pdfplumber first (better for tables)
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                if text.strip():
                    return text
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
        
        try:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return ""
    
    def extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return ""

