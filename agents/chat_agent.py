"""Chat agent for interactive GenAI chatbot."""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """Agent for handling chat interactions with applicants."""
    
    def __init__(self):
        super().__init__("ChatAgent")
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic - required by BaseAgent."""
        # ChatAgent doesn't modify state in the workflow
        # This method is here to satisfy the abstract base class
        return state
    
    def get_response(self, user_message: str, session_id: str,
                    context: Optional[Dict[str, Any]] = None) -> str:
        """Get response to user message."""
        # FACTUAL INFORMATION ABOUT THE SYSTEM (to prevent hallucinations)
        system_facts = """
CRITICAL SYSTEM INFORMATION - YOU MUST USE THIS ACCURATE INFORMATION:

REQUIRED DOCUMENTS:
1. Application Form (REQUIRED) - PDF or Image (PNG, JPG, JPEG)
   - This is the ONLY required document
   - Must be uploaded to start the application process

OPTIONAL DOCUMENTS (can be uploaded but not required):
2. Bank Statement - PDF or Image (PNG, JPG, JPEG)
3. Emirates ID - PDF or Image (PNG, JPG, JPEG)
4. Resume/CV - PDF or DOCX
5. Assets/Liabilities (Excel) - XLSX or XLS
6. Credit Report - PDF

APPLICATION PROCESS:
- Upload Application Form first (required)
- System extracts data from the form automatically
- You can review and edit extracted information
- Upload optional documents if available
- Submit application for processing
- Processing includes: data extraction, validation, eligibility assessment, and final decision

ELIGIBILITY FACTORS:
- Monthly income level
- Family/household size
- Employment status
- Assets and liabilities
- Credit history
- Overall financial situation

IMPORTANT RULES:
- ONLY Application Form is REQUIRED
- All other documents are OPTIONAL
- Do NOT make up document requirements
- Do NOT suggest documents that are not listed above
- If asked about documents, refer EXACTLY to the list above
"""
        
        system_prompt = f"""You are a helpful assistant for the Social Support Application system. 
You help applicants understand the application process, answer questions about their 
application status, and provide guidance on required documents and eligibility criteria.

{system_facts}

STRICT RULES:
1. When asked about required documents, ONLY mention Application Form as required
2. List optional documents clearly as "optional" or "not required"
3. Do NOT invent or hallucinate document requirements
4. Do NOT suggest documents that are not in the system
5. Be friendly, professional, and helpful
6. If you don't have specific information about an application, guide the user on how to find it
7. Base all answers on the factual information provided above"""
        
        # Build context-aware prompt
        user_prompt = user_message
        
        if context:
            if "application" in context:
                app = context["application"]
                user_prompt += f"\n\nApplication Context:\n"
                user_prompt += f"Application ID: {app.get('application_id', 'N/A')}\n"
                user_prompt += f"Status: {app.get('status', 'N/A')}\n"
                if app.get('created_at'):
                    user_prompt += f"Created: {app.get('created_at')}\n"
            
            if "extracted_data" in context:
                extracted = context["extracted_data"]
                if isinstance(extracted, dict) and "extracted_data" in extracted:
                    extracted = extracted["extracted_data"]
                user_prompt += f"\nExtracted data is available for reference."
                # Add key extracted fields for context
                if isinstance(extracted, dict):
                    app_form = extracted.get("application_form", {})
                    if app_form:
                        user_prompt += f"\nKey extracted information:"
                        if app_form.get("applicant_name"):
                            user_prompt += f"\n- Applicant Name: {app_form.get('applicant_name')}"
                        if app_form.get("income"):
                            user_prompt += f"\n- Income: {app_form.get('income')} AED/month"
                        if app_form.get("family_size"):
                            user_prompt += f"\n- Family Size: {app_form.get('family_size')}"
        
        response = self.call_llm_with_context(system_prompt, user_prompt)
        
        self.log_action("chat_response", {
            "session_id": session_id,
            "user_message_length": len(user_message)
        })
        
        return response

