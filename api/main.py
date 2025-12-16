"""FastAPI main application."""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import os
import shutil
from pathlib import Path
import logging

from agents.orchestrator import MasterOrchestrator
from database.postgres import PostgresDB
from database.mongodb import MongoDB
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional Redis import for session management
try:
    from database.redis_db import RedisDB
    redis_db = RedisDB()
    REDIS_AVAILABLE = True
    logger.info("Redis initialized for session management")
except Exception as e:
    logger.warning(f"Redis not available for session management: {e}")
    redis_db = None
    REDIS_AVAILABLE = False

app = FastAPI(title="Social Support Application API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
orchestrator = MasterOrchestrator()
postgres_db = PostgresDB()
mongodb = MongoDB()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)


class ChatMessage(BaseModel):
    """Chat message model."""
    application_id: Optional[str] = None
    message: str
    session_id: Optional[str] = None


class ApplicationResponse(BaseModel):
    """Application response model."""
    application_id: str
    status: str
    message: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Social Support Application API", "version": "1.0.0"}


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "orchestrator": "initialized"
        }
    }


@app.post("/api/v1/application/submit", response_model=ApplicationResponse)
async def submit_application(
    application_form: UploadFile = File(...),
    bank_statement: Optional[UploadFile] = File(None),
    emirates_id: Optional[UploadFile] = File(None),
    resume: Optional[UploadFile] = File(None),
    assets_liabilities: Optional[UploadFile] = File(None),
    credit_report: Optional[UploadFile] = File(None),
    edited_data: Optional[str] = Form(None)
):
    """Submit a new application with documents."""
    try:
        # Generate application ID
        application_id = f"APP-{uuid.uuid4().hex[:12].upper()}"
        
        # Save uploaded files
        documents = {}
        upload_path = Path(settings.upload_dir) / application_id
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Save application form (required)
        form_path = upload_path / f"application_form{Path(application_form.filename).suffix}"
        with open(form_path, "wb") as f:
            shutil.copyfileobj(application_form.file, f)
        documents["application_form"] = str(form_path)
        
        # Save optional documents
        optional_docs = {
            "bank_statement": bank_statement,
            "emirates_id": emirates_id,
            "resume": resume,
            "assets_liabilities": assets_liabilities,
            "credit_report": credit_report
        }
        
        for doc_type, file in optional_docs.items():
            if file:
                doc_path = upload_path / f"{doc_type}{Path(file.filename).suffix}"
                with open(doc_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                documents[doc_type] = str(doc_path)
        
        # Create application record
        postgres_db.create_application({
            "application_id": application_id,
            "applicant_name": "Extracted from form",
            "applicant_id": None,  # Will be extracted from documents
            "metadata": {
                "status": "processing",
                "documents_uploaded": list(documents.keys())
            }
        })
        
        # Store documents in MongoDB
        for doc_type, doc_path in documents.items():
            mongodb.store_document(application_id, doc_type, {
                "file_path": doc_path,
                "created_at": str(Path(doc_path).stat().st_mtime)
            })
        
        # Parse edited data if provided
        edited_data_dict = None
        if edited_data:
            try:
                import json
                edited_data_dict = json.loads(edited_data)
                logger.info(f"Received edited data for application {application_id}")
            except Exception as e:
                logger.warning(f"Could not parse edited_data: {e}")
        
        # Process application asynchronously (in production, use background tasks)
        try:
            result = orchestrator.process_application(application_id, documents, edited_data=edited_data_dict)
            
            # Store extracted data in MongoDB for frontend access
            if "extracted_data" in result:
                try:
                    mongodb.store_extracted_data(application_id, result["extracted_data"])
                except Exception as e:
                    logger.warning(f"Could not store extracted data: {e}")
            
            # Store validation results for frontend
            if "validation_results" in result:
                try:
                    # Store validation results alongside extracted data
                    existing_data = mongodb.get_extracted_data(application_id)
                    if existing_data:
                        existing_data["validation_results"] = result["validation_results"]
                        # Update the document
                        mongodb.db.extracted_data.update_one(
                            {"application_id": application_id},
                            {"$set": {"validation_results": result["validation_results"]}}
                        )
                except Exception as e:
                    logger.warning(f"Could not store validation results: {e}")
            
            # Update application status
            if result.get("status") == "completed":
                postgres_db.update_application_status(application_id, "completed")
                
                # Save eligibility assessment
                if "eligibility_assessment" in result:
                    assessment = result["eligibility_assessment"]
                    # Ensure all required fields are present
                    assessment_data = {
                        "application_id": application_id,
                        "income_level": assessment.get("income_level", "unknown"),
                        "employment_status": assessment.get("employment_status", "unknown"),
                        "family_size": assessment.get("family_size", 0),
                        "wealth_score": float(assessment.get("wealth_score", 0)),
                        "eligibility_score": float(assessment.get("eligibility_score", 0)),
                        "recommendation": assessment.get("recommendation", "pending"),
                        "reasoning": assessment.get("reasoning", "No reasoning provided")
                    }
                    postgres_db.save_eligibility_assessment(assessment_data)
                
                # Save final recommendation
                if "final_recommendation" in result:
                    postgres_db.save_final_recommendation(application_id, result["final_recommendation"])
            else:
                postgres_db.update_application_status(application_id, "failed")
        
        except Exception as e:
            logger.error(f"Processing error: {e}")
            postgres_db.update_application_status(application_id, "failed")
        
        return ApplicationResponse(
            application_id=application_id,
            status="submitted",
            message="Application submitted successfully. Processing in progress."
        )
    
    except Exception as e:
        logger.error(f"Submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/application/{application_id}")
async def get_application(application_id: str):
    """Get application status and results."""
    try:
        application = postgres_db.get_application(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Safely get extracted data from MongoDB
        extracted_data = None
        validation_results = None
        try:
            mongo_result = mongodb.get_extracted_data(application_id)
            if mongo_result:
                # Extract the nested extracted_data field
                extracted_data = mongo_result.get("extracted_data", {})
                validation_results = mongo_result.get("validation_results", {})
        except Exception as e:
            logger.warning(f"Could not retrieve extracted data: {e}")
        
        # Safely get documents
        documents = []
        try:
            documents = mongodb.get_documents(application_id)
        except Exception as e:
            logger.warning(f"Could not retrieve documents: {e}")
        
        # Safely get eligibility assessment from database
        eligibility_assessment = None
        try:
            eligibility_assessment = postgres_db.get_eligibility_assessment(application_id)
            # Convert to dict if it's a RealDictRow
            if eligibility_assessment:
                eligibility_assessment = dict(eligibility_assessment)
        except Exception as e:
            logger.warning(f"Could not retrieve eligibility assessment: {e}")
        
        # Safely get final recommendation from metadata
        final_recommendation = None
        try:
            final_recommendation = postgres_db.get_final_recommendation(application_id)
        except Exception as e:
            logger.warning(f"Could not retrieve final recommendation: {e}")
        
        # Convert application to dict and handle JSONB fields
        app_dict = dict(application) if application else {}
        # Handle metadata if it's a dict
        if "metadata" in app_dict and app_dict["metadata"]:
            if not isinstance(app_dict["metadata"], dict):
                try:
                    import json
                    if isinstance(app_dict["metadata"], str):
                        app_dict["metadata"] = json.loads(app_dict["metadata"])
                except:
                    app_dict["metadata"] = {}
        
        return {
            "application_id": application_id,
            "status": app_dict.get("status", "unknown"),
            "application": app_dict,
            "extracted_data": extracted_data,
            "validation_results": validation_results,
            "documents": documents,
            "eligibility_assessment": eligibility_assessment,
            "final_recommendation": final_recommendation
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving application: {str(e)}")


@app.post("/api/v1/chat")
async def chat(message: ChatMessage):
    """Chat with GenAI assistant with Redis session management."""
    try:
        from agents.chat_agent import ChatAgent
        
        chat_agent = ChatAgent()
        
        # Get or create session
        session_id = message.session_id or str(uuid.uuid4())
        
        # Get or create session data from Redis
        session_data = None
        if REDIS_AVAILABLE and redis_db:
            try:
                session_data = redis_db.get_session(session_id)
                if not session_data:
                    session_data = {
                        "session_id": session_id,
                        "messages": [],
                        "application_id": message.application_id,
                        "created_at": datetime.now().isoformat()
                    }
            except Exception as e:
                logger.warning(f"Error retrieving session from Redis: {e}")
                session_data = None
        
        # Get application context if available
        context = {}
        if message.application_id:
            application = postgres_db.get_application(message.application_id)
            if application:
                context["application"] = application
                extracted_data = mongodb.get_extracted_data(message.application_id)
                if extracted_data:
                    context["extracted_data"] = extracted_data
        
        # Get response from chat agent
        response = chat_agent.get_response(
            message.message,
            session_id=session_id,
            context=context
        )
        
        # Store chat history in Redis session
        if REDIS_AVAILABLE and redis_db and session_data:
            try:
                # Add message to session history
                if "messages" not in session_data:
                    session_data["messages"] = []
                
                session_data["messages"].append({
                    "role": "user",
                    "message": message.message,
                    "timestamp": datetime.now().isoformat()
                })
                session_data["messages"].append({
                    "role": "assistant",
                    "message": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Keep only last 50 messages to prevent session from growing too large
                if len(session_data["messages"]) > 50:
                    session_data["messages"] = session_data["messages"][-50:]
                
                # Update session in Redis (TTL: 2 hours)
                redis_db.set_session(session_id, session_data, ttl=7200)
                logger.debug(f"Updated session in Redis: {session_id}")
            except Exception as e:
                logger.warning(f"Error storing session in Redis: {e}")
        
        return {
            "response": response,
            "session_id": session_id
        }
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

