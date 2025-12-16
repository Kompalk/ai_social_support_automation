"""Main document processor for handling various document types."""
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from .text_extractor import TextExtractor
from .image_processor import ImageProcessor
from .tabular_processor import TabularProcessor

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes various document types (PDF, images, Excel, etc.)."""
    
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.image_processor = ImageProcessor()
        self.tabular_processor = TabularProcessor()
    
    def process_document(self, file_path: str, document_type: str) -> Dict[str, Any]:
        """
        Process a document based on its type.
        
        Args:
            file_path: Path to the document file
            document_type: Type of document (bank_statement, emirates_id, resume, 
                          assets_liabilities, credit_report, application_form)
        
        Returns:
            Dictionary containing extracted data
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if document_type == "bank_statement":
                return self._process_bank_statement(file_path)
            elif document_type == "emirates_id":
                return self._process_emirates_id(file_path)
            elif document_type == "resume":
                return self._process_resume(file_path)
            elif document_type == "assets_liabilities":
                return self._process_assets_liabilities(file_path)
            elif document_type == "credit_report":
                return self._process_credit_report(file_path)
            elif document_type == "application_form":
                return self._process_application_form(file_path)
            else:
                logger.warning(f"Unknown document type: {document_type}")
                return {"error": f"Unknown document type: {document_type}"}
        
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            return {"error": str(e)}
    
    def _process_bank_statement(self, file_path: str) -> Dict[str, Any]:
        """Extract data from bank statement (PDF or image)."""
        text = self.text_extractor.extract_from_pdf(file_path)
        if not text:
            # Try OCR if PDF extraction fails
            text = self.image_processor.extract_text_ocr(file_path)
        
        # Extract key information using patterns
        extracted_data = {
            "account_number": self._extract_pattern(text, r"Account\s+[Nn]o[.:]?\s*(\d+)"),
            "account_holder": self._extract_pattern(text, r"Account\s+[Hh]older[.:]?\s*([A-Za-z\s]+)"),
            "balance": self._extract_balance(text),
            "transactions": self._extract_transactions(text),
            "statement_period": self._extract_period(text),
            "raw_text": text
        }
        
        return {
            "document_type": "bank_statement",
            "extracted_data": extracted_data
        }
    
    def _process_emirates_id(self, file_path: str) -> Dict[str, Any]:
        """Extract data from Emirates ID (image)."""
        # Use OCR to extract text from ID image
        text = self.image_processor.extract_text_ocr(file_path)
        
        # Extract structured data
        extracted_data = {
            "id_number": self._extract_pattern(text, r"(\d{15})"),
            "name": self._extract_pattern(text, r"Name[:\s]+([A-Za-z\s]+)"),
            "nationality": self._extract_pattern(text, r"Nationality[:\s]+([A-Za-z\s]+)"),
            "date_of_birth": self._extract_pattern(text, r"(\d{2}[/-]\d{2}[/-]\d{4})"),
            "expiry_date": self._extract_pattern(text, r"Exp[.:]?\s*(\d{2}[/-]\d{2}[/-]\d{4})"),
            "raw_text": text
        }
        
        return {
            "document_type": "emirates_id",
            "extracted_data": extracted_data
        }
    
    def _process_resume(self, file_path: str) -> Dict[str, Any]:
        """Extract data from resume (PDF or DOCX)."""
        text = self.text_extractor.extract_from_pdf(file_path)
        if not text:
            text = self.text_extractor.extract_from_docx(file_path)
        
        extracted_data = {
            "name": self._extract_pattern(text, r"^([A-Z][a-z]+\s+[A-Z][a-z]+)", multiline=True),
            "email": self._extract_pattern(text, r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"),
            "phone": self._extract_pattern(text, r"(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})"),
            "education": self._extract_education(text),
            "experience": self._extract_experience(text),
            "skills": self._extract_skills(text),
            "raw_text": text
        }
        
        return {
            "document_type": "resume",
            "extracted_data": extracted_data
        }
    
    def _process_assets_liabilities(self, file_path: str) -> Dict[str, Any]:
        """Extract data from assets/liabilities Excel file."""
        data = self.tabular_processor.process_excel(file_path)
        
        extracted_data = {
            "assets": data.get("assets", []),
            "liabilities": data.get("liabilities", []),
            "total_assets": sum(item.get("value", 0) for item in data.get("assets", [])),
            "total_liabilities": sum(item.get("value", 0) for item in data.get("liabilities", [])),
            "net_worth": data.get("net_worth", 0)
        }
        
        return {
            "document_type": "assets_liabilities",
            "extracted_data": extracted_data
        }
    
    def _process_credit_report(self, file_path: str) -> Dict[str, Any]:
        """Extract data from credit report (PDF)."""
        text = self.text_extractor.extract_from_pdf(file_path)
        
        extracted_data = {
            "credit_score": self._extract_pattern(text, r"Credit\s+[Ss]core[:\s]+(\d+)"),
            "outstanding_debt": self._extract_amount(text, r"Outstanding\s+[Dd]ebt[:\s]+([\d,]+\.?\d*)"),
            "payment_history": self._extract_payment_history(text),
            "active_loans": self._extract_pattern(text, r"Active\s+[Ll]oans[:\s]+(\d+)"),
            "raw_text": text
        }
        
        return {
            "document_type": "credit_report",
            "extracted_data": extracted_data
        }
    
    def _process_application_form(self, file_path: str) -> Dict[str, Any]:
        """Extract data from application form (PDF or image)."""
        text = self.text_extractor.extract_from_pdf(file_path)
        if not text:
            text = self.image_processor.extract_text_ocr(file_path)
        
        extracted_data = {
            "applicant_name": self._extract_pattern(text, r"Name[:\s]+([A-Za-z\s]+)"),
            "address": self._extract_address(text),
            "income": self._extract_amount(text, r"Income[:\s]+([\d,]+\.?\d*)"),
            "family_size": self._extract_pattern(text, r"Family\s+[Ss]ize[:\s]+(\d+)"),
            "employment_status": self._extract_pattern(text, r"Employment[:\s]+([A-Za-z\s]+)"),
            "raw_text": text
        }
        
        return {
            "document_type": "application_form",
            "extracted_data": extracted_data
        }
    
    def _extract_pattern(self, text: str, pattern: str, multiline: bool = False) -> Optional[str]:
        """Extract text using regex pattern."""
        import re
        flags = re.MULTILINE | re.IGNORECASE if multiline else re.IGNORECASE
        match = re.search(pattern, text, flags)
        return match.group(1).strip() if match else None
    
    def _extract_balance(self, text: str) -> Optional[float]:
        """Extract account balance."""
        patterns = [
            r"Balance[:\s]+([\d,]+\.?\d*)",
            r"Available\s+Balance[:\s]+([\d,]+\.?\d*)"
        ]
        for pattern in patterns:
            match = self._extract_pattern(text, pattern)
            if match:
                try:
                    return float(match.replace(",", ""))
                except:
                    pass
        return None
    
    def _extract_amount(self, text: str, pattern: str) -> Optional[float]:
        """Extract monetary amount."""
        match = self._extract_pattern(text, pattern)
        if match:
            try:
                return float(match.replace(",", ""))
            except:
                pass
        return None
    
    def _extract_transactions(self, text: str) -> List[Dict[str, Any]]:
        """Extract transaction data from bank statement."""
        # Simplified extraction - in production, use more sophisticated parsing
        transactions = []
        # This would be enhanced with actual transaction parsing logic
        return transactions
    
    def _extract_period(self, text: str) -> Optional[str]:
        """Extract statement period."""
        return self._extract_pattern(text, r"Period[:\s]+([\d/\s-]+)")
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education information."""
        # Simplified - would use NLP for better extraction
        return []
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience."""
        # Simplified - would use NLP for better extraction
        return []
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume."""
        # Common skills keywords
        skills_keywords = ["Python", "Java", "SQL", "Management", "Communication"]
        found_skills = [skill for skill in skills_keywords if skill.lower() in text.lower()]
        return found_skills
    
    def _extract_address(self, text: str) -> Optional[str]:
        """Extract address information."""
        # Simplified address extraction - more flexible pattern
        return self._extract_pattern(text, r"Address[:\s]+([A-Za-z0-9\s,\-\.]+)")
    
    def _extract_payment_history(self, text: str) -> Dict[str, Any]:
        """Extract payment history from credit report."""
        return {
            "on_time_payments": self._extract_pattern(text, r"On[-\s]?time[:\s]+(\d+)"),
            "late_payments": self._extract_pattern(text, r"Late[:\s]+(\d+)")
        }

