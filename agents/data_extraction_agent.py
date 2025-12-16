"""Data extraction agent for extracting information from documents."""
from typing import Dict, Any
from .base_agent import BaseAgent
from data_processing.document_processor import DocumentProcessor
import logging

logger = logging.getLogger(__name__)


class DataExtractionAgent(BaseAgent):
    """Agent responsible for extracting data from uploaded documents."""
    
    def __init__(self):
        super().__init__("DataExtractionAgent")
        self.document_processor = DocumentProcessor()
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from all uploaded documents."""
        application_id = state.get("application_id")
        documents = state.get("documents", {})
        
        extracted_data = {}
        
        for doc_type, file_path in documents.items():
            try:
                logger.info(f"Extracting data from {doc_type}: {file_path}")
                result = self.document_processor.process_document(file_path, doc_type)
                extracted_data[doc_type] = result.get("extracted_data", {})
                
                # Use LLM to enhance extraction if needed
                if doc_type == "application_form":
                    extracted_data[doc_type] = self._enhance_extraction_with_llm(
                        extracted_data[doc_type]
                    )
                
            except Exception as e:
                logger.error(f"Error extracting from {doc_type}: {e}")
                extracted_data[doc_type] = {"error": str(e)}
        
        # Update state
        state["extracted_data"] = extracted_data
        state["extraction_status"] = "completed"
        
        self.log_action("extraction_completed", {
            "application_id": application_id,
            "documents_processed": len(documents)
        })
        
        return state
    
    def _enhance_extraction_with_llm(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to enhance and validate extracted data."""
        system_prompt = """You are a data extraction assistant. Review and enhance the extracted 
        data from an application form. Ensure all fields are properly extracted and formatted."""
        
        user_prompt = f"""Please review and enhance this extracted data:
        {extracted_data}
        
        Ensure:
        1. All personal information is correctly extracted
        2. Address information is complete
        3. Income and financial data is accurate
        4. Family information is properly structured
        
        Return the enhanced data in a structured format."""
        
        enhanced_text = self.call_llm_with_context(system_prompt, user_prompt)
        
        # In production, parse the LLM response into structured data
        # For now, we'll keep the original extracted data
        return extracted_data

