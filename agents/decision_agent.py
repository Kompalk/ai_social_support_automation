"""Final decision recommendation agent."""
from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class DecisionAgent(BaseAgent):
    """Agent responsible for final decision recommendation."""
    
    def __init__(self):
        super().__init__("DecisionAgent")
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final decision recommendation."""
        application_id = state.get("application_id")
        eligibility_assessment = state.get("eligibility_assessment", {})
        validation_results = state.get("validation_results", {})
        
        # Generate comprehensive decision
        decision = self._generate_decision(
            eligibility_assessment, validation_results
        )
        
        # Generate economic enablement recommendations
        enablement_recommendations = self._generate_enablement_recommendations(
            eligibility_assessment
        )
        
        final_recommendation = {
            "application_id": application_id,
            "decision": decision.get("decision", "pending"),
            "confidence": decision.get("confidence", 0.0),
            "reasoning": decision.get("reasoning", ""),
            "support_amount": decision.get("support_amount", 0),
            "support_type": decision.get("support_type", "financial"),
            "enablement_recommendations": enablement_recommendations,
            "next_steps": decision.get("next_steps", [])
        }
        
        # Update state
        state["final_recommendation"] = final_recommendation
        state["decision_status"] = "completed"
        state["status"] = "completed"
        
        self.log_action("decision_generated", {
            "application_id": application_id,
            "decision": final_recommendation["decision"]
        })
        
        return state
    
    def _generate_decision(self, eligibility_assessment: Dict[str, Any],
                          validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final decision using LLM reasoning."""
        system_prompt = """You are a decision-making expert for social support programs. 
        Based on eligibility assessments and validation results, make a final recommendation 
        for approval or decline. Consider all factors comprehensively and provide clear reasoning."""
        
        user_prompt = f"""Make a final decision for this application:
        
        Eligibility Assessment:
        - Eligibility Score: {eligibility_assessment.get('eligibility_score', 0)}
        - Income Level: {eligibility_assessment.get('income_level', 'N/A')}
        - Employment Status: {eligibility_assessment.get('employment_status', 'N/A')}
        - Family Size: {eligibility_assessment.get('family_size', 0)}
        - Wealth Score: {eligibility_assessment.get('wealth_score', 0)}
        - ML Recommendation: {eligibility_assessment.get('recommendation', 'N/A')}
        
        Validation Results:
        - Data Quality Score: {validation_results.get('data_quality_score', 0)}
        - Document Completeness: {validation_results.get('document_completeness', {}).get('completeness', 0)}
        
        LLM Assessment: {eligibility_assessment.get('llm_assessment', 'N/A')}
        
        Provide:
        1. Final decision (approve/conditional_approve/soft_decline/decline)
        2. Confidence level (0-1)
        3. Detailed reasoning
        4. Recommended support amount (if approved)
        5. Support type (financial/economic_enablement/both)
        6. Next steps for the applicant
        
        Format your response as a structured decision."""
        
        llm_response = self.call_llm_with_context(system_prompt, user_prompt)
        
        # Parse LLM response (simplified - in production, use structured output)
        decision = self._parse_decision_response(llm_response, eligibility_assessment)
        
        return decision
    
    def _parse_decision_response(self, llm_response: str,
                                eligibility_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM decision response."""
        # Simplified parsing - in production, use structured output or JSON parsing
        recommendation = eligibility_assessment.get("recommendation", "pending")
        score = eligibility_assessment.get("eligibility_score", 0.0)
        reasoning = eligibility_assessment.get("reasoning", "")
        
        # Determine support amount based on eligibility score and family size
        family_size = eligibility_assessment.get("family_size", 1)
        if recommendation == "approve":
            base_amount = 5000
            # Adjust for family size
            family_multiplier = 1 + (family_size - 1) * 0.2
            support_amount = base_amount * (1 + score) * family_multiplier
        elif recommendation == "conditional_approve":
            support_amount = 3000 * (1 + (family_size - 1) * 0.15)
        else:
            support_amount = 0
        
        # Build comprehensive reasoning
        detailed_reasoning = self._build_detailed_reasoning(
            recommendation, score, reasoning, llm_response, eligibility_assessment
        )
        
        return {
            "decision": recommendation,
            "confidence": min(score * 1.2, 1.0),  # Boost confidence slightly
            "reasoning": detailed_reasoning,
            "support_amount": int(support_amount),
            "support_type": "both" if score > 0.6 else "financial",
            "next_steps": self._generate_next_steps(recommendation)
        }
    
    def _build_detailed_reasoning(self, recommendation: str, score: float,
                                  eligibility_reasoning: str, llm_response: str,
                                  eligibility_assessment: Dict[str, Any]) -> str:
        """Build comprehensive reasoning for the decision."""
        reasoning_parts = []
        
        # Decision summary
        reasoning_parts.append(f"DECISION: {recommendation.upper().replace('_', ' ')}")
        reasoning_parts.append(f"Eligibility Score: {score:.2%}")
        
        # Key factors
        reasoning_parts.append("\nKEY FACTORS:")
        reasoning_parts.append(f"- Income Level: {eligibility_assessment.get('income_level', 'N/A')}")
        reasoning_parts.append(f"- Family Size: {eligibility_assessment.get('family_size', 'N/A')}")
        reasoning_parts.append(f"- Employment Status: {eligibility_assessment.get('employment_status', 'N/A')}")
        reasoning_parts.append(f"- Wealth Score: {eligibility_assessment.get('wealth_score', 0):.2f}")
        
        # Eligibility reasoning
        if eligibility_reasoning:
            reasoning_parts.append(f"\nELIGIBILITY ASSESSMENT:\n{eligibility_reasoning}")
        
        # LLM insights (truncated if too long)
        if llm_response:
            llm_summary = llm_response[:300] + "..." if len(llm_response) > 300 else llm_response
            reasoning_parts.append(f"\nADDITIONAL CONSIDERATIONS:\n{llm_summary}")
        
        # Decision rationale
        reasoning_parts.append(f"\nDECISION RATIONALE:")
        if recommendation == "approve":
            reasoning_parts.append("The applicant demonstrates significant financial need based on low income, "
                                 "large family size, and limited assets. Approval is recommended to provide "
                                 "essential social support.")
        elif recommendation == "conditional_approve":
            reasoning_parts.append("The applicant shows moderate financial need. Conditional approval is recommended "
                                 "with additional verification of circumstances.")
        elif recommendation == "soft_decline":
            reasoning_parts.append("While the applicant may not qualify for direct financial support, they may benefit "
                                 "from economic enablement programs such as job training and career counseling.")
        else:
            reasoning_parts.append("The applicant's financial situation does not meet the current eligibility criteria "
                                 "for social support programs.")
        
        return "\n".join(reasoning_parts)
    
    def _generate_next_steps(self, decision: str) -> list:
        """Generate next steps based on decision."""
        if decision == "approve":
            return [
                "Application approved",
                "Awaiting final verification",
                "Support will be disbursed within 5 business days"
            ]
        elif decision == "conditional_approve":
            return [
                "Conditional approval granted",
                "Additional documentation may be required",
                "Review in progress"
            ]
        elif decision == "soft_decline":
            return [
                "Application requires review",
                "Applicant may reapply with additional information",
                "Consider economic enablement programs"
            ]
        else:
            return [
                "Application declined",
                "Applicant may appeal the decision",
                "Consider alternative support programs"
            ]
    
    def _generate_enablement_recommendations(self, 
                                           eligibility_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate economic enablement recommendations."""
        system_prompt = """You are an economic enablement advisor. Based on applicant profile, 
        recommend upskilling opportunities, job matching, and career counseling."""
        
        user_prompt = f"""Generate economic enablement recommendations:
        
        Applicant Profile:
        - Employment Status: {eligibility_assessment.get('employment_status', 'N/A')}
        - Education Level: {eligibility_assessment.get('education_level', 'N/A')}
        - Skills: {eligibility_assessment.get('skills', [])}
        - Income Level: {eligibility_assessment.get('income_level', 'N/A')}
        
        Provide recommendations for:
        1. Upskilling and training opportunities
        2. Job matching suggestions
        3. Career counseling needs
        4. Professional development programs"""
        
        llm_response = self.call_llm_with_context(system_prompt, user_prompt)
        
        return {
            "upskilling_opportunities": self._extract_upskilling_recommendations(llm_response),
            "job_matching": self._extract_job_matching(llm_response),
            "career_counseling": self._extract_career_counseling(llm_response),
            "full_recommendations": llm_response
        }
    
    def _extract_upskilling_recommendations(self, text: str) -> list:
        """Extract upskilling recommendations from LLM response."""
        # Simplified extraction
        recommendations = []
        if "training" in text.lower():
            recommendations.append("Professional training programs")
        if "certification" in text.lower():
            recommendations.append("Industry certifications")
        if "skill" in text.lower():
            recommendations.append("Skills development workshops")
        return recommendations if recommendations else ["General upskilling programs"]
    
    def _extract_job_matching(self, text: str) -> list:
        """Extract job matching suggestions."""
        return ["Job matching services", "Career placement assistance"]
    
    def _extract_career_counseling(self, text: str) -> list:
        """Extract career counseling recommendations."""
        return ["Career counseling sessions", "Professional development guidance"]

