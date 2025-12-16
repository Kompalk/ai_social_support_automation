"""Streamlit frontend application."""
import streamlit as st
import requests
import uuid
from typing import Dict, Any
import time
from streamlit_chat import message
import json
import tempfile
import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from data_processing.document_processor import DocumentProcessor

# Setup logging
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Social Support Application",
    page_icon="🤝",
    layout="wide"
)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "application_id" not in st.session_state:
    st.session_state.application_id = None

if "application_status" not in st.session_state:
    st.session_state.application_status = None

if "extracted_data_editable" not in st.session_state:
    st.session_state.extracted_data_editable = {}

if "show_confetti" not in st.session_state:
    st.session_state.show_confetti = False

if "processing_status" not in st.session_state:
    st.session_state.processing_status = None

if "show_editable_data" not in st.session_state:
    st.session_state.show_editable_data = False


def submit_application(files: Dict[str, Any], edited_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Submit application to API."""
    try:
        files_to_send = {}
        for key, file in files.items():
            if file is not None:
                files_to_send[key] = (file.name, file.getvalue(), file.type)
        
        # Add edited data as JSON if available
        data = {}
        if edited_data:
            data["edited_data"] = json.dumps(edited_data)
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/application/submit",
            files=files_to_send,
            data=data,
            timeout=300
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error submitting application: {str(e)}")
        return None


def get_application_status(application_id: str) -> Dict[str, Any]:
    """Get application status from API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/application/{application_id}",
            timeout=30
        )
        if response.status_code == 404:
            st.error("❌ This ID does not exist. Please check your ID again.")
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.error("❌ This ID does not exist. Please check your ID again.")
        else:
            st.error(f"Error retrieving application: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error retrieving application: {str(e)}")
        return None


def send_chat_message(user_message: str, application_id: str = None) -> str:
    """Send chat message to API."""
    try:
        payload = {
            "message": user_message,
            "session_id": st.session_state.session_id,
            "application_id": application_id
        }
        response = requests.post(
            f"{API_BASE_URL}/api/v1/chat",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "I'm sorry, I couldn't process your request.")
    except Exception as e:
        return f"Error: {str(e)}"


def generate_decision_explanation(final_rec: Dict[str, Any], eligibility_assessment: Dict[str, Any]) -> str:
    """Generate applicant-facing decision explanation using LLM."""
    try:
        decision = final_rec.get("decision", "pending")
        reasoning = final_rec.get("reasoning", "")
        support_amount = final_rec.get("support_amount", 0)
        next_steps = final_rec.get("next_steps", [])
        
        # Get key information from eligibility assessment
        income_level = eligibility_assessment.get("income_level", "N/A")
        family_size = eligibility_assessment.get("family_size", "N/A")
        employment_status = eligibility_assessment.get("employment_status", "N/A")
        
        # Map decision to format
        decision_map = {
            "approve": "APPROVED",
            "conditional_approve": "UNDER REVIEW",
            "soft_decline": "UNDER REVIEW",
            "decline": "DECLINED",
            "pending": "UNDER REVIEW"
        }
        final_decision = decision_map.get(decision, "UNDER REVIEW")
        
        # Build prompt for LLM
        system_prompt = """You are an AI assistant generating an APPLICANT-FACING decision explanation
for a social support eligibility system.

Your task is to explain the FINAL DECISION clearly, respectfully, and
consistently, based ONLY on the provided decision outcome and policy reason.

STRICT RULES (MUST FOLLOW):
1. Output EXACTLY ONE final decision.
2. Do NOT include internal scores, model details, or technical jargon.
3. Do NOT contradict the final decision in any part of the response.
4. Use neutral, empathetic, and policy-focused language.
5. Do NOT make recommendations that override policy.
6. Keep the explanation concise and structured.
7. Assume the reader is non-technical.

OUTPUT FORMAT (MUST MATCH EXACTLY):

Final Decision: <APPROVED | DECLINED | UNDER REVIEW>

---

Reason for Decision

<One short paragraph clearly explaining the primary policy reason for the decision.
Mention income, household size, or other policy factors only if relevant.
Do not repeat numbers unless necessary for clarity.>

---

Key Information Reviewed

- <Key factor 1>
- <Key factor 2>
- <Key factor 3>

---

What This Means

<One short paragraph explaining the implication of the decision in simple terms.
Do not restate the reason. Do not mention AI or scoring.>

---

Next Steps Available to You

- <Next step 1>
- <Next step 2>
- <Next step 3>

CONTENT GUIDELINES:
- The "Reason for Decision" must explicitly reference the policy rule applied
  (e.g., income threshold exceeded).
- The "Key Information Reviewed" section must list only factors actually used.
- The "What This Means" section must be calm and non-judgmental.
- The "Next Steps" section must never imply approval if the decision is DECLINED.

If the decision is DECLINED:
- Mention appeal and reapplication options.
- Do NOT suggest approval or conditional approval.

If the decision is APPROVED:
- Mention next administrative steps only.

If the decision is UNDER REVIEW:
- Clearly state that no final decision has been made yet.

Do not add any extra sections.
Do not add a summary.
Do not include emojis.
Do not include headings other than those specified above."""

        user_prompt = f"""Generate the decision explanation for:

Final Decision: {final_decision}
Policy Reason: {reasoning}
Income Level: {income_level}
Family Size: {family_size}
Employment Status: {employment_status}
Support Amount (if approved): {support_amount:,.0f} AED
Next Steps (if provided): {', '.join(next_steps) if next_steps else 'Standard process steps'}

Generate the explanation following the exact format specified."""

        # Call LLM via chat API
        payload = {
            "message": f"{system_prompt}\n\n{user_prompt}",
            "session_id": st.session_state.session_id,
            "application_id": None
        }
        response = requests.post(
            f"{API_BASE_URL}/api/v1/chat",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        explanation = result.get("response", "")
        
        return explanation
        
    except Exception as e:
        logger.error(f"Error generating decision explanation: {e}")
        return None


def main():
    """Main application."""
    # Sidebar for navigation
    st.sidebar.title("🤝 Social Support")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        ["New Application", "Application Status", "Chat Assistant"],
        label_visibility="visible"
    )
    
    st.sidebar.markdown("---")
    if st.session_state.application_id:
        st.sidebar.info(f"**Application ID:**\n{st.session_state.application_id}")
    
    # Render selected page
    if page == "New Application":
        render_new_application()
    elif page == "Application Status":
        render_application_status()
    elif page == "Chat Assistant":
        render_chat_assistant()


def render_new_application():
    """Render new application form."""
    st.title("📝 Submit New Application")
    st.markdown("Please upload the required documents to submit your application.")
    st.markdown("---")
    
    # Upload Application Form button
    if st.button("📄 Upload Application Form", use_container_width=True, type="primary"):
        st.session_state["show_uploader"] = True
    
    # Show uploader if button clicked or if file already uploaded
    show_uploader = st.session_state.get("show_uploader", False) or st.session_state.get("application_form_file") is not None
    
    application_form = None
    if show_uploader:
        application_form = st.file_uploader(
            "Application Form (PDF/Image)",
            type=["pdf", "png", "jpg", "jpeg"],
            help="Upload your completed application form",
            key="app_form_uploader"
        )
    
    # Store file in session state immediately when uploaded
    if application_form is not None:
        st.session_state["application_form_file"] = application_form
    
    # Extract and show editable form immediately after application form upload
    extracted_app_data = None
    if application_form is not None:
        # Check if we need to extract (avoid re-extracting on every rerun)
        file_key = f"app_form_{application_form.name}_{application_form.size}"
        if st.session_state.get("last_extracted_file_key") != file_key:
            with st.spinner("Extracting data from application form..."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(application_form.name).suffix) as tmp_file:
                        tmp_file.write(application_form.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Extract data using DocumentProcessor
                    processor = DocumentProcessor()
                    result = processor.process_document(tmp_path, "application_form")
                    extracted_app_data = result.get("extracted_data", {})
                    
                    # Store in session state
                    st.session_state["extracted_app_form_data"] = extracted_app_data
                    st.session_state["last_extracted_file_key"] = file_key
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                except Exception as e:
                    st.warning(f"Could not extract data from application form: {e}")
                    extracted_app_data = None
        else:
            # Use cached extracted data
            extracted_app_data = st.session_state.get("extracted_app_form_data")
    
    # Show editable form if data was extracted, or warning if form not uploaded
    if extracted_app_data:
        st.markdown("---")
        # Check if form was saved (collapsed state)
        form_saved = st.session_state.get("app_form_saved", False)
        with st.expander("📝 Review & Edit Application Information", expanded=not form_saved):
            st.info("Please review and edit the extracted application information before submitting.")
            display_editable_application_info_from_extraction(extracted_app_data)
            
            # Note about using edited data
            if st.session_state.get("preview_edited_data"):
                st.success("✅ Your edited information will be used for eligibility assessment.")
    elif show_uploader and application_form is None:
        st.warning("⚠️ Please upload an Application Form to extract and review your information.")
    
    # Form for optional documents and submission
    with st.form("application_form"):
        st.subheader("Optional Documents")
        col1, col2 = st.columns(2)
        
        with col1:
            bank_statement = st.file_uploader(
                "Bank Statement",
                type=["pdf", "png", "jpg", "jpeg"],
                help="Upload your bank statement"
            )
            
            emirates_id = st.file_uploader(
                "Emirates ID",
                type=["pdf", "png", "jpg", "jpeg"],
                help="Upload a copy of your Emirates ID"
            )
            
            resume = st.file_uploader(
                "Resume/CV",
                type=["pdf", "docx"],
                help="Upload your resume or CV"
            )
        
        with col2:
            assets_liabilities = st.file_uploader(
                "Assets/Liabilities (Excel)",
                type=["xlsx", "xls"],
                help="Upload your assets and liabilities spreadsheet"
            )
            
            credit_report = st.file_uploader(
                "Credit Report",
                type=["pdf"],
                help="Upload your credit report"
            )
        
        submitted = st.form_submit_button("Submit Application", use_container_width=True)
    
    # Handle submission outside the form to avoid nesting
    if submitted:
        # Reset processing complete flag for new submission
        st.session_state["processing_complete"] = False
        
        # Get application form from session state if available, otherwise use current upload
        app_form_to_submit = st.session_state.get("application_form_file") or application_form
        
        if not app_form_to_submit:
            st.error("Please upload an application form (required)")
        else:
            files = {
                "application_form": app_form_to_submit,
                "bank_statement": bank_statement,
                "emirates_id": emirates_id,
                "resume": resume,
                "assets_liabilities": assets_liabilities,
                "credit_report": credit_report
            }
            
            # Get edited data if available (use edited data instead of extracted)
            edited_data = st.session_state.get("preview_edited_data")
            
            # Show processing UI BEFORE submission
            st.markdown("---")
            st.markdown("### Processing Your Application")
            
            # Animated progress bar with CSS blinking effect (blink only, no shimmer)
            # We'll use a session state flag to control when to stop blinking
            processing_complete = st.session_state.get("processing_complete", False)
            
            if not processing_complete:
                st.markdown("""
                <style>
                @keyframes blink {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.4; }
                }
                .stProgress > div > div > div {
                    animation: blink 1.5s ease-in-out infinite;
                }
                </style>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <style>
                .stProgress > div > div > div {
                    animation: none;
                }
                </style>
                """, unsafe_allow_html=True)
            
            # Create progress bar and status placeholder (for inverse order stacking)
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            
            # Initialize list to store messages (will be displayed in reverse)
            status_messages_list = []
            
            # Status messages for progression (with validation details)
            status_messages = [
                ("📄 Extracting data from documents...", 0.15),
                ("✅ Validating information across documents...", 0.25),
                ("🔍 Checking name consistency across all documents...", 0.40),
                ("✅ Verifying address and personal details match...", 0.55),
                ("💰 Assessing eligibility based on financial data...", 0.70),
                ("📊 Generating recommendation and support amount...", 0.85),
                ("✨ Finalizing assessment...", 0.95)
            ]
            
            # Show initial progress immediately (stacked, latest at top)
            status_messages_list.append(status_messages[0][0])
            # Display in reverse order (latest at top)
            messages_html = "".join([f'<div style="margin-bottom: 0.5rem;">ℹ️ {msg}</div>' for msg in reversed(status_messages_list)])
            status_placeholder.markdown(messages_html, unsafe_allow_html=True)
            progress_bar.progress(status_messages[0][1])
            time.sleep(0.5)  # Brief pause
            
            # Show progress steps progressively (stacked in inverse order, latest at top)
            # Update progress bar to show steps as processing occurs
            for message, progress in status_messages[1:]:
                status_messages_list.append(message)
                # Display all messages in reverse order (latest at top)
                messages_html = "".join([f'<div style="margin-bottom: 0.5rem;">{msg}</div>' for msg in reversed(status_messages_list)])
                status_placeholder.markdown(messages_html, unsafe_allow_html=True)
                progress_bar.progress(progress)
                time.sleep(1.0)  # Realistic delay between steps (simulates processing time)
            
            # Submit application (this will take time - blocking call)
            # Progress bar already shows all steps, API processes in background
            result = submit_application(files, edited_data)
            
            if result:
                st.session_state.application_id = result.get("application_id")
                
                # Check for extracted data
                status_data = get_application_status(st.session_state.application_id)
                
                if status_data:
                    extracted_data = status_data.get("extracted_data")
                    current_status = status_data.get("status", "processing")
                    
                    # Handle nested structure from MongoDB
                    actual_extracted_data = extracted_data
                    if isinstance(extracted_data, dict) and "extracted_data" in extracted_data:
                        actual_extracted_data = extracted_data["extracted_data"]
                    
                    # Complete progress
                    progress_bar.progress(1.0)
                    
                    # Mark processing as complete to stop blinking
                    st.session_state["processing_complete"] = True
                    
                    # Stop blinking animation
                    st.markdown("""
                    <style>
                    .stProgress > div > div > div {
                        animation: none !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Show completion message (messages are already stacked above in reverse order)
                    completion_html = '<div style="margin-bottom: 1rem;"><h4>✅ Processing Complete - All Steps Finished!</h4></div>'
                    completion_html += '<div style="margin-bottom: 0.5rem; color: green;">✓ All processing steps have been completed successfully.</div>'
                    # Show all messages in reverse order (latest at top)
                    completion_html += "".join([f'<div style="margin-bottom: 0.5rem;">ℹ️ {msg}</div>' for msg in reversed(status_messages_list)])
                    status_placeholder.markdown(completion_html, unsafe_allow_html=True)
                    
                    # Show balloons at the END (after all processing)
                    st.balloons()
                    
                    st.success(f"🎉 Application submitted successfully!")
                    st.info(f"Application ID: **{st.session_state.application_id}**")
                    
                    # Don't show duplicate edit form here - it's already shown before submission
                    if current_status != "completed":
                        st.info("⏳ Processing continues in background. Check status in the 'Application Status' page.")
                else:
                    progress_bar.progress(0.9)
                    st.warning("⚠️ Could not retrieve application status. Please try again.")
                    
                    if st.button("🔄 Retry", use_container_width=True, key="retry_status"):
                        st.rerun()
    
    # Show editable data if it was set in session state
    if st.session_state.get("show_editable_data") and st.session_state.application_id:
        status_data = get_application_status(st.session_state.application_id)
        if status_data:
            extracted_data = status_data.get("extracted_data")
            if isinstance(extracted_data, dict) and "extracted_data" in extracted_data:
                extracted_data = extracted_data["extracted_data"]
            if extracted_data:
                display_editable_application_info(extracted_data, status_data)


def render_application_status():
    """Render application status page."""
    st.title("📊 Application Status")
    st.markdown("---")
    
    # Application ID input (no autofill)
    app_id_input = st.text_input(
        "Enter Application ID",
        value="",
        placeholder="APP-XXXXXXXXXXXX",
        key="status_app_id"
    )
    
    check_button = st.button("Check Status", use_container_width=True, type="primary")
    
    if check_button or (st.session_state.application_id and app_id_input == st.session_state.application_id):
        application_id = app_id_input.strip() or st.session_state.application_id
        
        if not application_id:
            st.warning("⚠️ Please enter an application ID")
        else:
            with st.spinner("Retrieving application status..."):
                status_data = get_application_status(application_id)
                
                if status_data:
                    st.session_state.application_id = application_id
                    st.session_state.application_status = status_data
                    
                    # Display status
                    status = status_data.get("status", "unknown")
                    
                    st.markdown("### Application Status")
                    if status == "completed":
                        st.success(f"✅ **{status.upper()}**")
                    elif status == "processing":
                        st.info(f"⏳ **{status.upper()}**")
                    elif status == "failed":
                        st.error(f"❌ **{status.upper()}**")
                    else:
                        st.warning(f"⚠️ **{status.upper()}**")
                    
                    st.markdown("---")
                    
                    # Display application details
                    st.markdown("### Application Details")
                    application = status_data.get("application", {})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Application ID", application_id)
                    with col2:
                        st.metric("Status", status.title())
                    with col3:
                        created_at = application.get("created_at", "N/A")
                        display_date = created_at[:10] if len(created_at) > 10 else created_at
                        st.metric("Created", display_date)
                    
                    # Display applicant name (not editable)
                    applicant_name = application.get("applicant_name", "Not available")
                    if applicant_name and applicant_name != "Extracted from form":
                        st.info(f"**Applicant Name:** {applicant_name}")
                    
                    # Display eligibility status if available
                    eligibility_assessment = status_data.get("eligibility_assessment")
                    if eligibility_assessment or status == "completed":
                        st.markdown("---")
                        st.markdown("### Eligibility Assessment")
                        
                        if eligibility_assessment:
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                eligibility_score = eligibility_assessment.get("eligibility_score", 0)
                                # Display as percentage
                                score_display = f"{eligibility_score:.1%}"
                                st.metric("Eligibility Score", score_display)
                            
                            with col2:
                                income_level = eligibility_assessment.get("income_level", "N/A")
                                st.metric("Income Level", income_level.replace("_", " ").title())
                            
                            with col3:
                                family_size = eligibility_assessment.get("family_size", "N/A")
                                st.metric("Family Size", family_size)
                            
                            with col4:
                                recommendation = eligibility_assessment.get("recommendation", "N/A")
                                rec_display = recommendation.replace("_", " ").title()
                                if recommendation == "approve":
                                    st.success(f"**{rec_display}**")
                                elif recommendation == "decline":
                                    st.error(f"**{rec_display}**")
                                else:
                                    st.warning(f"**{rec_display}**")
                            
                            # Show final recommendation details if available
                            final_rec = status_data.get("final_recommendation")
                            if final_rec:
                                st.markdown("---")
                                st.markdown("### Final Decision & Explanation")
                                
                                # Generate applicant-facing explanation using LLM
                                decision_explanation = generate_decision_explanation(
                                    final_rec, eligibility_assessment
                                )
                                
                                if decision_explanation:
                                    st.markdown(decision_explanation)
                                else:
                                    # Fallback if LLM generation fails
                                    decision = final_rec.get("decision", "pending")
                                    decision_display = decision.replace("_", " ").title()
                                    if decision == "approve":
                                        st.success(f"**Decision: {decision_display}**")
                                    elif decision == "decline":
                                        st.error(f"**Decision: {decision_display}**")
                                    else:
                                        st.warning(f"**Decision: {decision_display}**")
                        else:
                            st.info("Eligibility assessment is being processed...")


def display_editable_application_info_from_extraction(app_form_data: Dict[str, Any]):
    """Display application form information in editable form from raw extracted data."""
    if not app_form_data:
        st.warning("No extracted data available.")
        return
    
    # Show editable form fields (read-only display, not a form to avoid nesting)
    st.markdown("#### Application Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Name
        default_name = app_form_data.get("applicant_name", "") or app_form_data.get("name", "")
        edited_name = st.text_input(
            "Full Name",
            value=default_name,
            key="preview_name"
        )
        
        # Email
        default_email = app_form_data.get("email", "")
        edited_email = st.text_input(
            "Email",
            value=default_email,
            key="preview_email"
        )
        
        # Phone
        default_phone = app_form_data.get("phone", "") or app_form_data.get("phone_number", "")
        edited_phone = st.text_input(
            "Phone Number",
            value=default_phone,
            key="preview_phone"
        )
    
    with col2:
        # Income
        default_income = app_form_data.get("income", "") or app_form_data.get("monthly_income", "")
        edited_income = st.text_input(
            "Monthly Income (AED)",
            value=str(default_income) if default_income else "",
            key="preview_income"
        )
        
        # Family Size
        default_family_size = app_form_data.get("family_size", "") or app_form_data.get("household_size", "")
        try:
            family_size_val = int(default_family_size) if default_family_size else 1
        except:
            family_size_val = 1
        edited_family_size = st.number_input(
            "Family Size",
            min_value=1,
            max_value=20,
            value=family_size_val,
            key="preview_family_size"
        )
        
        # Employment Status
        default_employment = app_form_data.get("employment_status", "")
        employment_options = ["Employed", "Unemployed", "Part-time", "Self-employed", "Student", "Retired"]
        try:
            emp_index = employment_options.index(default_employment) if default_employment in employment_options else 0
        except:
            emp_index = 0
        edited_employment = st.selectbox(
            "Employment Status",
            options=employment_options,
            index=emp_index,
            key="preview_employment"
        )
    
    # Address
    st.markdown("#### Address")
    default_address = app_form_data.get("address", "")
    edited_address = st.text_area(
        "Address",
        value=default_address,
        key="preview_address",
        height=100
    )
    
    # Store edited values in session state for later use
    st.session_state["preview_edited_data"] = {
        "name": edited_name,
        "email": edited_email,
        "phone": edited_phone,
        "income": edited_income,
        "family_size": edited_family_size,
        "employment_status": edited_employment,
        "address": edited_address
    }
    
    # Save button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("💾 Save", use_container_width=True, type="primary", key="save_preview_data"):
            st.session_state["app_form_saved"] = True
            st.success("✅ Application information saved!")
            st.rerun()


def display_editable_application_info(extracted_data: Dict[str, Any], status_data: Dict[str, Any]):
    """Display only application form information in editable form (not all documents)."""
    if not extracted_data:
        st.warning("No extracted data available yet.")
        return
    
    # Handle different data structures
    if isinstance(extracted_data, dict) and "extracted_data" in extracted_data:
        extracted_data = extracted_data["extracted_data"]
    
    # Get ONLY application form data (not other documents)
    app_form_data = extracted_data.get("application_form", {}) if isinstance(extracted_data, dict) else {}
    
    # If no application_form, try to get data from root level
    if not app_form_data and isinstance(extracted_data, dict):
        if "applicant_name" in extracted_data or "name" in extracted_data:
            app_form_data = extracted_data
    
    # Show editable form (NOT nested in another form)
    with st.form("edit_application_info", clear_on_submit=False):
        st.markdown("#### Application Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Name
            default_name = app_form_data.get("applicant_name", "") or app_form_data.get("name", "")
            edited_name = st.text_input(
                "Full Name",
                value=default_name,
                key="edit_name"
            )
            
            # Email
            default_email = app_form_data.get("email", "")
            edited_email = st.text_input(
                "Email",
                value=default_email,
                key="edit_email"
            )
            
            # Phone
            default_phone = app_form_data.get("phone", "") or app_form_data.get("phone_number", "")
            edited_phone = st.text_input(
                "Phone Number",
                value=default_phone,
                key="edit_phone"
            )
        
        with col2:
            # Income
            default_income = app_form_data.get("income", "") or app_form_data.get("monthly_income", "")
            edited_income = st.text_input(
                "Monthly Income (AED)",
                value=str(default_income) if default_income else "",
                key="edit_income"
            )
            
            # Family Size
            default_family_size = app_form_data.get("family_size", "") or app_form_data.get("household_size", "")
            edited_family_size = st.number_input(
                "Family Size",
                min_value=1,
                max_value=20,
                value=int(default_family_size) if default_family_size else 1,
                key="edit_family_size"
            )
            
            # Employment Status
            default_employment = app_form_data.get("employment_status", "")
            employment_options = ["Employed", "Unemployed", "Part-time", "Self-employed", "Student", "Retired"]
            edited_employment = st.selectbox(
                "Employment Status",
                options=employment_options,
                index=employment_options.index(default_employment) if default_employment in employment_options else 0,
                key="edit_employment"
            )
        
        # Address
        st.markdown("#### Address")
        default_address = app_form_data.get("address", "")
        edited_address = st.text_area(
            "Address",
            value=default_address,
            key="edit_address",
            height=100
        )
        
        # Submit edited data
        save_button = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
        
        if save_button:
            # Store edited data (in a real app, this would be sent to API)
            edited_data = {
                "name": edited_name,
                "email": edited_email,
                "phone": edited_phone,
                "income": edited_income,
                "family_size": edited_family_size,
                "employment_status": edited_employment,
                "address": edited_address
            }
            st.session_state.extracted_data_editable = edited_data
            st.success("✅ Changes saved! (Note: In production, this would update the application)")


def render_chat_assistant():
    """Render chat assistant interface."""
    st.title("💬 Chat Assistant")
    st.markdown("Ask questions about your application or get help with the process.")
    st.markdown("---")
    
    # Application ID context (editable)
    app_id_context = st.text_input(
        "Application ID (optional - for context)",
        value=st.session_state.application_id or "",
        placeholder="APP-XXXXXXXXXXXX",
        key="chat_app_id"
    )
    if app_id_context and app_id_context != st.session_state.application_id:
        st.session_state.application_id = app_id_context
    
    st.markdown("---")
    
    # Chat interface
    st.markdown("### Chat")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, chat in enumerate(st.session_state.chat_history):
            if chat["role"] == "user":
                message(chat["message"], is_user=True, key=f"user_{i}")
            else:
                message(chat["message"], is_user=False, key=f"assistant_{i}")
    
    st.markdown("---")
    
    # Chat input with form to clear after sending
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Type your message...",
            key="chat_input",
            placeholder="Ask about your application, required documents, or eligibility..."
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            send_button = st.form_submit_button("Send", use_container_width=True, type="primary")
    
    if send_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "message": user_input
        })
        
        # Get response
        with st.spinner("Thinking..."):
            response = send_chat_message(
                user_input,
                st.session_state.application_id if st.session_state.application_id else None
            )
        
        # Add assistant response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "message": response
        })
        
        # Rerun to update chat display (form already clears input)
        st.rerun()
    
    # Quick action buttons
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("What documents do I need?"):
            response = send_chat_message("What documents are required for the application?")
            st.session_state.chat_history.append({"role": "user", "message": "What documents do I need?"})
            st.session_state.chat_history.append({"role": "assistant", "message": response})
            st.rerun()
    
    with col2:
        if st.button("Check my application status"):
            if st.session_state.application_id:
                response = send_chat_message(
                    f"What is the status of application {st.session_state.application_id}?",
                    st.session_state.application_id
                )
                st.session_state.chat_history.append({"role": "user", "message": "Check my application status"})
                st.session_state.chat_history.append({"role": "assistant", "message": response})
                st.rerun()
            else:
                st.warning("Please enter an Application ID above")
    
    with col3:
        if st.button("Eligibility criteria"):
            response = send_chat_message("What are the eligibility criteria for social support?")
            st.session_state.chat_history.append({"role": "user", "message": "Eligibility criteria"})
            st.session_state.chat_history.append({"role": "assistant", "message": response})
            st.rerun()


if __name__ == "__main__":
    main()