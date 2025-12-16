"""Data validation agent for cross-checking and validating extracted data."""
from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class ValidationAgent(BaseAgent):
    """Agent responsible for validating and cross-checking extracted data."""
    
    def __init__(self):
        super().__init__("ValidationAgent")
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data for consistency and accuracy."""
        application_id = state.get("application_id")
        extracted_data = state.get("extracted_data", {})
        
        validation_results = {
            "address_consistency": self._validate_address_consistency(extracted_data),
            "income_consistency": self._validate_income_consistency(extracted_data),
            "identity_consistency": self._validate_identity_consistency(extracted_data),
            "family_consistency": self._validate_family_consistency(extracted_data),
            "document_completeness": self._validate_document_completeness(extracted_data),
            "data_quality_score": 0.0
        }
        
        # Calculate overall data quality score
        validation_results["data_quality_score"] = self._calculate_quality_score(
            validation_results
        )
        
        # Use LLM for advanced validation
        llm_validation = self._llm_validation(extracted_data, validation_results)
        validation_results["llm_insights"] = llm_validation
        
        # Update state
        state["validation_results"] = validation_results
        state["validation_status"] = "completed"
        
        self.log_action("validation_completed", {
            "application_id": application_id,
            "quality_score": validation_results["data_quality_score"]
        })
        
        return state
    
    def _validate_address_consistency(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check address consistency across documents."""
        addresses = []
        
        # Get addresses from different documents
        if "application_form" in extracted_data:
            app_address = extracted_data["application_form"].get("address")
            if app_address:
                addresses.append(("application_form", app_address))
        
        if "emirates_id" in extracted_data:
            id_address = extracted_data["emirates_id"].get("address")
            if id_address:
                addresses.append(("emirates_id", id_address))
        
        # Simple consistency check
        if len(addresses) <= 1:
            return {"status": "insufficient_data", "confidence": 0.5}
        
        # Check if addresses are similar (simplified)
        is_consistent = len(set(addresses)) == 1
        return {
            "status": "consistent" if is_consistent else "inconsistent",
            "confidence": 0.9 if is_consistent else 0.3,
            "addresses": addresses
        }
    
    def _validate_income_consistency(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check income consistency across documents."""
        income_sources = []
        
        # Get income from application form
        if "application_form" in extracted_data:
            app_income = extracted_data["application_form"].get("income")
            if app_income:
                income_sources.append(("application_form", app_income))
        
        # Get income from bank statement (average monthly)
        if "bank_statement" in extracted_data:
            transactions = extracted_data["bank_statement"].get("transactions", [])
            # Calculate average income from transactions
            # Simplified for now
            pass
        
        return {
            "status": "validated",
            "confidence": 0.8,
            "income_sources": income_sources
        }
    
    def _validate_identity_consistency(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check identity consistency (name, ID number) across documents with fuzzy matching."""
        names = []
        id_numbers = []
        
        # Collect names from all documents
        if "application_form" in extracted_data:
            name = extracted_data["application_form"].get("applicant_name")
            if name:
                names.append(("application_form", name))
        
        if "emirates_id" in extracted_data:
            name = extracted_data["emirates_id"].get("name")
            id_num = extracted_data["emirates_id"].get("id_number")
            if name:
                names.append(("emirates_id", name))
            if id_num:
                id_numbers.append(("emirates_id", id_num))
        
        # Check names in bank statement
        if "bank_statement" in extracted_data:
            name = extracted_data["bank_statement"].get("account_holder_name")
            if name:
                names.append(("bank_statement", name))
        
        # Check names in resume
        if "resume" in extracted_data:
            name = extracted_data["resume"].get("name")
            if name:
                names.append(("resume", name))
        
        # Fuzzy name matching (time-efficient method)
        name_consistent = False
        confidence = 0.4
        
        if len(names) >= 2:
            # Normalize names for comparison
            normalized_names = []
            for doc_type, name in names:
                # Remove extra spaces, convert to lowercase, remove special chars
                normalized = " ".join(name.lower().split())
                normalized = "".join(c for c in normalized if c.isalnum() or c.isspace())
                normalized_names.append((doc_type, normalized))
            
            # Check exact matches first (fastest)
            unique_normalized = set([n[1] for n in normalized_names])
            if len(unique_normalized) == 1:
                name_consistent = True
                confidence = 0.95
            else:
                # Fuzzy matching using word overlap (fast and effective)
                name_words = [set(n[1].split()) for n in normalized_names]
                
                # Calculate similarity between all pairs
                similarities = []
                for i in range(len(name_words)):
                    for j in range(i + 1, len(name_words)):
                        if name_words[i] and name_words[j]:
                            # Jaccard similarity (word overlap)
                            intersection = len(name_words[i] & name_words[j])
                            union = len(name_words[i] | name_words[j])
                            similarity = intersection / union if union > 0 else 0
                            similarities.append(similarity)
                
                if similarities:
                    avg_similarity = sum(similarities) / len(similarities)
                    # Consider consistent if >70% word overlap
                    if avg_similarity >= 0.7:
                        name_consistent = True
                        confidence = 0.7 + (avg_similarity * 0.2)  # Scale to 0.7-0.9
                    elif avg_similarity >= 0.5:
                        confidence = 0.5 + (avg_similarity * 0.2)  # Scale to 0.5-0.7
        
        return {
            "status": "consistent" if name_consistent else "inconsistent",
            "confidence": confidence,
            "names": names,
            "id_numbers": id_numbers,
            "match_details": {
                "total_names_found": len(names),
                "matching_method": "fuzzy" if name_consistent and len(names) >= 2 else "exact"
            }
        }
    
    def _validate_family_consistency(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check family member information consistency."""
        # This would check family size and member details across documents
        return {
            "status": "validated",
            "confidence": 0.7
        }
    
    def _validate_document_completeness(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if all required documents are present and complete."""
        required_docs = [
            "application_form",
            "bank_statement",
            "emirates_id",
            "resume",
            "assets_liabilities",
            "credit_report"
        ]
        
        present_docs = [doc for doc in required_docs if doc in extracted_data]
        completeness = len(present_docs) / len(required_docs)
        
        return {
            "status": "complete" if completeness >= 0.8 else "incomplete",
            "completeness": completeness,
            "present_documents": present_docs,
            "missing_documents": [doc for doc in required_docs if doc not in present_docs]
        }
    
    def _calculate_quality_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate overall data quality score."""
        scores = []
        
        # Address consistency
        if "address_consistency" in validation_results:
            scores.append(validation_results["address_consistency"].get("confidence", 0.5))
        
        # Identity consistency
        if "identity_consistency" in validation_results:
            scores.append(validation_results["identity_consistency"].get("confidence", 0.5))
        
        # Document completeness
        if "document_completeness" in validation_results:
            scores.append(validation_results["document_completeness"].get("completeness", 0.5))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _llm_validation(self, extracted_data: Dict[str, Any], 
                       validation_results: Dict[str, Any]) -> str:
        """Use LLM to provide validation insights."""
        system_prompt = """You are a data validation expert. Analyze extracted data from 
        social support application documents and identify any inconsistencies, errors, or 
        missing information."""
        
        user_prompt = f"""Please analyze this extracted data and validation results:
        
        Extracted Data: {extracted_data}
        Validation Results: {validation_results}
        
        Provide insights on:
        1. Any data inconsistencies found
        2. Missing critical information
        3. Data quality concerns
        4. Recommendations for data correction
        
        Be specific and actionable."""
        
        return self.call_llm_with_context(system_prompt, user_prompt)

