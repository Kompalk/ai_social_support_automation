"""Eligibility assessment agent."""
from typing import Dict, Any
from .base_agent import BaseAgent
from models.eligibility_model import EligibilityModel
import logging

logger = logging.getLogger(__name__)


class EligibilityAgent(BaseAgent):
    """Agent responsible for assessing applicant eligibility."""
    
    def __init__(self):
        super().__init__("EligibilityAgent")
        self.eligibility_model = EligibilityModel()
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Assess eligibility based on extracted and validated data."""
        application_id = state.get("application_id")
        extracted_data = state.get("extracted_data", {})
        validation_results = state.get("validation_results", {})
        
        # Prepare features for ML model
        features = self._extract_features(extracted_data)
        
        # Explicit high-income rejection check BEFORE model prediction
        monthly_income = features.get("monthly_income", 0) or features.get("income", 0)
        household_size = features.get("household_size", 1) or features.get("family_size", 1)
        income_per_capita = monthly_income / max(1, household_size)
        
        # Hard rejection for very high income (policy-based)
        if monthly_income > 50000 or income_per_capita > 25000:
            # Force NOT_ELIGIBLE tier regardless of model prediction
            ml_prediction = {
                "support_tier": "NOT_ELIGIBLE",
                "confidence": 1.0,
                "policy_action": "REJECT",
                "rejection_reason": f"High income threshold exceeded (Income: {monthly_income:,.0f} AED/month, Per Capita: {income_per_capita:,.0f} AED)"
            }
        else:
            # Get ML model prediction for normal cases
            ml_prediction = self.eligibility_model.predict(features)
        
        # Calculate eligibility score from ML prediction
        # Convert support_tier to numeric score (0.0 to 1.0)
        support_tier = ml_prediction.get("support_tier", "NOT_ELIGIBLE")
        confidence = ml_prediction.get("confidence", 0.0)
        
        # Map tier to base score
        tier_scores = {
            "HIGH": 0.85,
            "MEDIUM": 0.65,
            "LOW": 0.45,
            "NOT_ELIGIBLE": 0.05  # Reduced from 0.15 to 0.05 for clearer rejection
        }
        base_score = tier_scores.get(support_tier, 0.05)
        
        # Adjust score based on confidence, but cap NOT_ELIGIBLE scores
        if support_tier == "NOT_ELIGIBLE":
            # For NOT_ELIGIBLE, don't let confidence inflate the score
            # Use lower weight for confidence to keep score low
            eligibility_score = (base_score * 0.9) + (confidence * 0.1)
            # Cap at maximum 15% for NOT_ELIGIBLE
            eligibility_score = min(eligibility_score, 0.15)
        else:
            # For eligible tiers, use normal weighting
            eligibility_score = (base_score * 0.7) + (confidence * 0.3)
        
        # Add eligibility_score to ml_prediction for consistency
        ml_prediction["eligibility_score"] = eligibility_score
        
        # Get LLM-based assessment
        llm_assessment = self._llm_eligibility_assessment(
            extracted_data, validation_results, features
        )
        
        # Generate recommendation based on eligibility score
        recommendation = self._generate_recommendation(ml_prediction, llm_assessment)
        
        # Generate detailed reasoning
        reasoning = self._generate_reasoning(
            features, eligibility_score, recommendation, ml_prediction, llm_assessment
        )
        
        eligibility_result = {
            "application_id": application_id,
            "income_level": self._categorize_income(features.get("income", 0)),
            "employment_status": features.get("employment_status", "unknown"),
            "family_size": features.get("family_size", 0),
            "wealth_score": self._calculate_wealth_score(extracted_data),
            "eligibility_score": eligibility_score,
            "ml_prediction": ml_prediction,
            "llm_assessment": llm_assessment,
            "recommendation": recommendation,
            "reasoning": reasoning
        }
        
        # Update state
        state["eligibility_assessment"] = eligibility_result
        state["eligibility_status"] = "completed"
        
        self.log_action("eligibility_assessed", {
            "application_id": application_id,
            "eligibility_score": eligibility_result["eligibility_score"]
        })
        
        return state
    
    def _extract_features(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from extracted data for ML model."""
        features = {}
        
        # Income
        if "application_form" in extracted_data:
            app_data = extracted_data["application_form"]
            # Ensure income is numeric
            income = app_data.get("income", 0)
            if isinstance(income, str):
                try:
                    income = float(income.replace(",", "").replace("AED", "").strip())
                except:
                    income = 0
            features["income"] = float(income) if income else 0
            # Also set monthly_income for model compatibility
            features["monthly_income"] = features["income"]
            
            features["employment_status"] = app_data.get("employment_status", "unknown")
            
            # Ensure family_size is integer
            family_size = app_data.get("family_size", 0)
            if isinstance(family_size, str):
                try:
                    family_size = int(family_size)
                except:
                    family_size = 0
            features["family_size"] = int(family_size) if family_size else 0
            # Also set household_size for model compatibility
            features["household_size"] = features["family_size"]
        
        # Wealth assessment
        if "assets_liabilities" in extracted_data:
            assets_data = extracted_data["assets_liabilities"]
            # Ensure all values are numeric
            net_worth = assets_data.get("net_worth", 0)
            if isinstance(net_worth, str):
                try:
                    net_worth = float(net_worth.replace(",", "").replace("AED", "").strip())
                except:
                    net_worth = 0
            features["net_worth"] = float(net_worth) if net_worth else 0
            
            total_assets = assets_data.get("total_assets", 0)
            if isinstance(total_assets, str):
                try:
                    total_assets = float(total_assets.replace(",", "").replace("AED", "").strip())
                except:
                    total_assets = 0
            features["total_assets"] = float(total_assets) if total_assets else 0
            
            total_liabilities = assets_data.get("total_liabilities", 0)
            if isinstance(total_liabilities, str):
                try:
                    total_liabilities = float(total_liabilities.replace(",", "").replace("AED", "").strip())
                except:
                    total_liabilities = 0
            features["total_liabilities"] = float(total_liabilities) if total_liabilities else 0
            
            # Calculate assets_to_liabilities ratio for model
            if total_liabilities > 0:
                features["assets_to_liabilities"] = total_assets / total_liabilities
            else:
                features["assets_to_liabilities"] = 1.0 if total_assets > 0 else 0.6
        
        # Credit score
        if "credit_report" in extracted_data:
            credit_data = extracted_data["credit_report"]
            # Ensure credit_score is numeric
            credit_score = credit_data.get("credit_score", 0)
            if isinstance(credit_score, str):
                try:
                    credit_score = int(credit_score)
                except:
                    credit_score = 0
            features["credit_score"] = int(credit_score) if credit_score else 0
            
            # Ensure outstanding_debt is numeric
            outstanding_debt = credit_data.get("outstanding_debt", 0)
            if isinstance(outstanding_debt, str):
                try:
                    outstanding_debt = float(outstanding_debt.replace(",", "").replace("AED", "").strip())
                except:
                    outstanding_debt = 0
            features["outstanding_debt"] = float(outstanding_debt) if outstanding_debt else 0
            
            # Calculate debt_to_income ratio for model
            if features.get("income", 0) > 0:
                features["debt_to_income"] = outstanding_debt / (features["income"] * 12)  # Annual debt / annual income
            else:
                features["debt_to_income"] = 0.3  # Default
        
        # Employment history from resume
        if "resume" in extracted_data:
            resume_data = extracted_data["resume"]
            features["has_work_experience"] = len(resume_data.get("experience", [])) > 0
            features["education_level"] = self._assess_education_level(
                resume_data.get("education", [])
            )
        
        # Calculate employment_stability for model (0-1 scale)
        employment_status = features.get("employment_status", "unknown").lower()
        if employment_status in ["unemployed", "unemployed"]:
            features["employment_stability"] = 0.2
        elif employment_status in ["part-time", "part time"]:
            features["employment_stability"] = 0.5
        elif employment_status in ["employed", "full-time", "full time"]:
            features["employment_stability"] = 0.9
        else:
            features["employment_stability"] = 0.7  # Default moderate stability
        
        # Set defaults for missing required features
        if "monthly_income" not in features:
            features["monthly_income"] = features.get("income", 0)
        if "household_size" not in features:
            features["household_size"] = features.get("family_size", 1)
        if "debt_to_income" not in features:
            features["debt_to_income"] = 0.3
        if "employment_stability" not in features:
            features["employment_stability"] = 0.7
        if "assets_to_liabilities" not in features:
            features["assets_to_liabilities"] = 0.6
        
        return features
    
    def _categorize_income(self, income: float) -> str:
        """Categorize income level."""
        if income < 5000:
            return "very_low"
        elif income < 10000:
            return "low"
        elif income < 20000:
            return "medium"
        elif income < 50000:
            return "high"
        else:
            return "very_high"
    
    def _calculate_wealth_score(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate wealth assessment score."""
        if "assets_liabilities" not in extracted_data:
            return 0.0
        
        assets_data = extracted_data["assets_liabilities"]
        net_worth = assets_data.get("net_worth", 0)
        
        # Normalize to 0-100 scale
        if net_worth < 0:
            return 0.0
        elif net_worth > 1000000:
            return 100.0
        else:
            return (net_worth / 10000)  # Simplified scoring
    
    def _assess_education_level(self, education: list) -> str:
        """Assess education level from resume."""
        if not education:
            return "unknown"
        
        # Simplified assessment
        education_text = " ".join(education).lower()
        if "phd" in education_text or "doctorate" in education_text:
            return "phd"
        elif "master" in education_text or "mba" in education_text:
            return "masters"
        elif "bachelor" in education_text or "degree" in education_text:
            return "bachelors"
        elif "diploma" in education_text:
            return "diploma"
        else:
            return "high_school"
    
    def _generate_recommendation(self, ml_prediction: Dict[str, Any], 
                                llm_assessment: str) -> str:
        """Generate recommendation based on assessments."""
        score = ml_prediction.get("eligibility_score", 0.0)
        
        # Adjusted thresholds for social support (more lenient)
        if score >= 0.6:
            return "approve"
        elif score >= 0.45:
            return "conditional_approve"
        elif score >= 0.3:
            return "soft_decline"
        else:
            return "decline"
    
    def _generate_reasoning(self, features: Dict[str, Any], eligibility_score: float,
                           recommendation: str, ml_prediction: Dict[str, Any],
                           llm_assessment: str) -> str:
        """Generate detailed reasoning for the eligibility assessment."""
        # Ensure all values are properly typed
        income = float(features.get("income", 0) or features.get("monthly_income", 0) or 0)
        family_size = int(features.get("family_size", 0) or features.get("household_size", 1) or 1)
        net_worth = float(features.get("net_worth", 0) or 0)
        credit_score = int(features.get("credit_score", 0) or 0)
        employment_status = str(features.get("employment_status", "unknown"))
        
        reasoning_parts = []
        
        # Check for high-income rejection reason
        if "rejection_reason" in ml_prediction:
            reasoning_parts.append(f"Policy Rejection: {ml_prediction['rejection_reason']}")
        
        # Score explanation
        reasoning_parts.append(f"Eligibility Score: {eligibility_score:.2%}")
        
        # Income analysis
        income_per_capita = income / max(1, family_size)
        if income > 50000 or income_per_capita > 25000:
            reasoning_parts.append(f"Income Level: Very High ({income:,.0f} AED/month, {income_per_capita:,.0f} AED per capita) - Exceeds eligibility threshold for social support")
        elif income < 5000:
            reasoning_parts.append(f"Income Level: Very Low ({income:,.0f} AED/month) - Strong indicator of financial need")
        elif income < 10000:
            reasoning_parts.append(f"Income Level: Low ({income:,.0f} AED/month) - Indicates financial need")
        elif income < 20000:
            reasoning_parts.append(f"Income Level: Moderate ({income:,.0f} AED/month)")
        else:
            reasoning_parts.append(f"Income Level: High ({income:,.0f} AED/month) - May exceed eligibility thresholds")
        
        # Family size analysis
        if family_size >= 4:
            reasoning_parts.append(f"Family Size: Large ({family_size} members) - Higher support need")
        elif family_size >= 2:
            reasoning_parts.append(f"Family Size: Medium ({family_size} members)")
        else:
            reasoning_parts.append(f"Family Size: Small ({family_size} member)")
        
        # Employment analysis
        if employment_status.lower() in ["unemployed", "unemployed"]:
            reasoning_parts.append("Employment Status: Unemployed - High priority for support")
        elif employment_status.lower() in ["part-time", "part time"]:
            reasoning_parts.append("Employment Status: Part-time - Moderate need")
        else:
            reasoning_parts.append(f"Employment Status: {employment_status}")
        
        # Net worth analysis
        if net_worth < 0:
            reasoning_parts.append(f"Net Worth: Negative ({net_worth:,.0f} AED) - Significant financial distress")
        elif net_worth < 10000:
            reasoning_parts.append(f"Net Worth: Very Low ({net_worth:,.0f} AED) - Limited financial resources")
        else:
            reasoning_parts.append(f"Net Worth: {net_worth:,.0f} AED")
        
        # Credit score analysis
        if credit_score < 600:
            reasoning_parts.append(f"Credit Score: Low ({credit_score}) - May indicate financial difficulties")
        elif credit_score < 700:
            reasoning_parts.append(f"Credit Score: Moderate ({credit_score})")
        else:
            reasoning_parts.append(f"Credit Score: Good ({credit_score})")
        
        # Recommendation explanation
        if recommendation == "approve":
            reasoning_parts.append("Recommendation: APPROVE - Applicant meets eligibility criteria for social support")
        elif recommendation == "conditional_approve":
            reasoning_parts.append("Recommendation: CONDITIONAL APPROVE - Applicant may qualify with additional verification")
        elif recommendation == "soft_decline":
            reasoning_parts.append("Recommendation: SOFT DECLINE - Applicant may benefit from economic enablement programs")
        else:
            reasoning_parts.append("Recommendation: DECLINE - Applicant does not meet current eligibility criteria")
        
        # Key factors
        feature_importance = ml_prediction.get("feature_importance", {})
        if feature_importance:
            top_factor = max(feature_importance.items(), key=lambda x: x[1])
            reasoning_parts.append(f"Primary Factor: {top_factor[0].replace('_', ' ').title()} (weight: {top_factor[1]:.2%})")
        
        return " | ".join(reasoning_parts)
    
    def _llm_eligibility_assessment(self, extracted_data: Dict[str, Any],
                                   validation_results: Dict[str, Any],
                                   features: Dict[str, Any]) -> str:
        """Use LLM for comprehensive eligibility assessment."""
        system_prompt = """You are an eligibility assessment expert for social support programs. 
        Analyze applicant data and provide a comprehensive eligibility assessment considering:
        1. Income level and financial need
        2. Employment status and history
        3. Family size and dependents
        4. Assets and liabilities
        5. Credit history
        6. Overall financial situation
        
        Provide a detailed assessment with reasoning."""
        
        user_prompt = f"""Assess eligibility for this application:
        
        Extracted Data Summary:
        - Income: {features.get('income', 'N/A')}
        - Employment Status: {features.get('employment_status', 'N/A')}
        - Family Size: {features.get('family_size', 'N/A')}
        - Net Worth: {features.get('net_worth', 'N/A')}
        - Credit Score: {features.get('credit_score', 'N/A')}
        
        Validation Quality Score: {validation_results.get('data_quality_score', 0)}
        
        Provide:
        1. Eligibility assessment
        2. Key factors influencing the decision
        3. Recommendations for support type and amount
        4. Economic enablement opportunities (upskilling, job matching, etc.)"""
        
        return self.call_llm_with_context(system_prompt, user_prompt)

