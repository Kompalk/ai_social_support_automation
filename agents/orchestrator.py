"""Master orchestrator agent using LangGraph for workflow orchestration."""
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
try:
    from langfuse.decorators import langfuse_context, observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    # Create dummy decorators if langfuse not available
    def observe(func=None, **kwargs):
        """Dummy observe decorator that works with or without parentheses."""
        if func is None:
            # Called as @observe() - return a decorator
            def decorator(f):
                return f
            return decorator
        else:
            # Called as @observe - return the function directly
            return func
    langfuse_context = type('obj', (object,), {'update_current_trace': lambda *args, **kwargs: None})()

from .base_agent import BaseAgent
from .data_extraction_agent import DataExtractionAgent
from .validation_agent import ValidationAgent
from .eligibility_agent import EligibilityAgent
from .decision_agent import DecisionAgent
import logging

logger = logging.getLogger(__name__)


class ApplicationState(TypedDict, total=False):
    """State structure for the application workflow."""
    application_id: str
    documents: Dict[str, str]
    extracted_data: Dict[str, Any]
    validation_results: Dict[str, Any]
    eligibility_assessment: Dict[str, Any]
    final_recommendation: Dict[str, Any]
    extraction_status: str
    validation_status: str
    eligibility_status: str
    decision_status: str
    edited_data: Dict[str, Any]  # Optional edited data from frontend
    status: str
    error: str


class MasterOrchestrator:
    """Master orchestrator using LangGraph for agent coordination."""
    
    def __init__(self):
        self.extraction_agent = DataExtractionAgent()
        self.validation_agent = ValidationAgent()
        self.eligibility_agent = EligibilityAgent()
        self.decision_agent = DecisionAgent()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow with ReAct reasoning pattern."""
        workflow = StateGraph(ApplicationState)
        
        # Add nodes
        workflow.add_node("extract", self._extract_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("assess_eligibility", self._assess_eligibility_node)
        workflow.add_node("make_decision", self._make_decision_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Define workflow edges
        workflow.set_entry_point("extract")
        
        # Add conditional edges with ReAct reasoning
        workflow.add_conditional_edges(
            "extract",
            self._should_continue_after_extraction,
            {
                "continue": "validate",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "validate",
            self._should_continue_after_validation,
            {
                "continue": "assess_eligibility",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "assess_eligibility",
            self._should_continue_after_eligibility,
            {
                "continue": "make_decision",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("make_decision", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    @observe()
    def _extract_node(self, state: ApplicationState) -> ApplicationState:
        """Extract data from documents."""
        try:
            langfuse_context.update_current_trace(
                name="data_extraction",
                metadata={"application_id": state.get("application_id")}
            )
            
            updated_state = self.extraction_agent.execute(state)
            
            # Merge edited data with extracted data if available
            # Edited data overrides extracted data for application_form
            edited_data = state.get("edited_data")
            if edited_data and "extracted_data" in updated_state:
                if "application_form" in updated_state["extracted_data"]:
                    # Merge edited data into application_form extracted data
                    app_form_data = updated_state["extracted_data"]["application_form"]
                    # Map edited fields to extracted data structure
                    if "name" in edited_data:
                        app_form_data["applicant_name"] = edited_data["name"]
                    if "email" in edited_data:
                        app_form_data["email"] = edited_data["email"]
                    if "phone" in edited_data:
                        app_form_data["phone"] = edited_data["phone"]
                        app_form_data["phone_number"] = edited_data["phone"]
                    if "income" in edited_data:
                        try:
                            app_form_data["income"] = float(edited_data["income"]) if edited_data["income"] else None
                            app_form_data["monthly_income"] = float(edited_data["income"]) if edited_data["income"] else None
                        except:
                            pass
                    if "family_size" in edited_data:
                        try:
                            app_form_data["family_size"] = int(edited_data["family_size"]) if edited_data["family_size"] else None
                            app_form_data["household_size"] = int(edited_data["family_size"]) if edited_data["family_size"] else None
                        except:
                            pass
                    if "employment_status" in edited_data:
                        app_form_data["employment_status"] = edited_data["employment_status"]
                    if "address" in edited_data:
                        app_form_data["address"] = edited_data["address"]
                    
                    logger.info(f"Merged edited data into extracted_data for application {state.get('application_id')}")
            
            return updated_state
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            state["error"] = str(e)
            state["extraction_status"] = "failed"
            return state
    
    @observe()
    def _validate_node(self, state: ApplicationState) -> ApplicationState:
        """Validate extracted data."""
        try:
            langfuse_context.update_current_trace(
                name="data_validation",
                metadata={"application_id": state.get("application_id")}
            )
            
            updated_state = self.validation_agent.execute(state)
            return updated_state
        except Exception as e:
            logger.error(f"Validation error: {e}")
            state["error"] = str(e)
            state["validation_status"] = "failed"
            return state
    
    @observe()
    def _assess_eligibility_node(self, state: ApplicationState) -> ApplicationState:
        """Assess eligibility."""
        try:
            langfuse_context.update_current_trace(
                name="eligibility_assessment",
                metadata={"application_id": state.get("application_id")}
            )
            
            updated_state = self.eligibility_agent.execute(state)
            return updated_state
        except Exception as e:
            logger.error(f"Eligibility assessment error: {e}")
            state["error"] = str(e)
            state["eligibility_status"] = "failed"
            return state
    
    @observe()
    def _make_decision_node(self, state: ApplicationState) -> ApplicationState:
        """Make final decision."""
        try:
            langfuse_context.update_current_trace(
                name="decision_making",
                metadata={"application_id": state.get("application_id")}
            )
            
            updated_state = self.decision_agent.execute(state)
            return updated_state
        except Exception as e:
            logger.error(f"Decision making error: {e}")
            state["error"] = str(e)
            state["decision_status"] = "failed"
            return state
    
    def _handle_error_node(self, state: ApplicationState) -> ApplicationState:
        """Handle errors in the workflow."""
        logger.error(f"Workflow error for {state.get('application_id')}: {state.get('error')}")
        state["status"] = "failed"
        return state
    
    def _should_continue_after_extraction(self, state: ApplicationState) -> str:
        """ReAct reasoning: Should we continue after extraction?"""
        if state.get("error") or state.get("extraction_status") == "failed":
            return "error"
        
        extracted_data = state.get("extracted_data", {})
        if not extracted_data:
            return "error"
        
        return "continue"
    
    def _should_continue_after_validation(self, state: ApplicationState) -> str:
        """ReAct reasoning: Should we continue after validation?"""
        if state.get("error") or state.get("validation_status") == "failed":
            return "error"
        
        validation_results = state.get("validation_results", {})
        quality_score = validation_results.get("data_quality_score", 0)
        
        # Continue even with lower quality, but flag it
        if quality_score < 0.3:
            return "error"
        
        return "continue"
    
    def _should_continue_after_eligibility(self, state: ApplicationState) -> str:
        """ReAct reasoning: Should we continue after eligibility assessment?"""
        if state.get("error") or state.get("eligibility_status") == "failed":
            return "error"
        
        return "continue"
    
    @observe()
    def process_application(self, application_id: str, 
                          documents: Dict[str, str],
                          edited_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a complete application through the workflow."""
        try:
            langfuse_context.update_current_trace(
                name="application_processing",
                metadata={"application_id": application_id}
            )
            
            # Initialize state
            initial_state: ApplicationState = {
                "application_id": application_id,
                "documents": documents,
                "extracted_data": {},
                "validation_results": {},
                "eligibility_assessment": {},
                "final_recommendation": {},
                "extraction_status": "pending",
                "validation_status": "pending",
                "eligibility_status": "pending",
                "decision_status": "pending",
                "status": "processing",
                "error": "",
                "edited_data": edited_data  # Store edited data in state
            }
            
            # Execute workflow
            final_state = self.workflow.invoke(initial_state)
            
            return dict(final_state)
        
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            return {
                "application_id": application_id,
                "status": "failed",
                "error": str(e)
            }

