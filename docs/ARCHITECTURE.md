# System Architecture

## Overview
The Social Support Application Workflow Automation system is built using a microservices-inspired architecture with AI agents orchestrated through LangGraph.

## Components

### 1. Data Processing Layer
- **Document Processor**: Handles multimodal data (PDF, images, Excel)
- **Text Extractor**: Extracts text from PDFs and DOCX files
- **Image Processor**: OCR capabilities for images and scanned documents
- **Tabular Processor**: Processes Excel files for assets/liabilities

### 2. AI Agents Layer

#### Master Orchestrator
- Coordinates all agents using LangGraph
- Implements ReAct reasoning pattern
- Manages workflow state and error handling

#### Data Extraction Agent
- Extracts structured data from documents
- Uses LLM to enhance extraction accuracy
- Processes all document types

#### Validation Agent
- Cross-checks data consistency across documents
- Validates address, income, identity information
- Calculates data quality scores

#### Eligibility Agent
- Assesses eligibility using ML models and LLM
- Combines ML predictions with LLM reasoning
- Generates eligibility scores and recommendations

#### Decision Agent
- Makes final approval/decline recommendations
- Generates economic enablement suggestions
- Provides detailed reasoning

#### Chat Agent
- Handles interactive conversations
- Provides application assistance
- Answers questions about status and process

### 3. ML Models
- **Eligibility Model**: RandomForest Classifier
- Trained on synthetic data with explainability features
- Provides eligibility scores (support tiers: HIGH/MEDIUM/LOW/NOT_ELIGIBLE) and feature importance

### 4. Database Layer
- **PostgreSQL**: Structured application data, eligibility assessments, application metadata
- **MongoDB**: Unstructured document storage, extracted data, validation results
- **Redis**: Caching (eligibility assessments), session management, chat history

### 5. API Layer (FastAPI)
- RESTful endpoints for application submission
- Chat API for GenAI interactions
- Application status retrieval
- Health checks

### 6. Frontend (Streamlit)
- New application submission interface
- Application status dashboard
- Interactive chat assistant
- Document upload and management

## Workflow

1. **Application Submission**
   - User uploads documents via Streamlit
   - Documents stored in file system and MongoDB
   - Application record created in PostgreSQL

2. **Data Extraction**
   - Documents processed by Document Processor
   - Data Extraction Agent extracts structured information
   - Extracted data stored in MongoDB

3. **Validation**
   - Validation Agent cross-checks data consistency
   - Address, income, identity validation
   - Quality score calculated

4. **Eligibility Assessment**
   - Features extracted for ML model
   - ML model predicts eligibility score
   - LLM provides comprehensive assessment
   - Results combined for final assessment

5. **Decision Making**
   - Decision Agent generates final recommendation
   - Economic enablement opportunities identified
   - Reasoning and next steps provided

6. **Results**
   - Final recommendation stored in PostgreSQL
   - User can view status via Streamlit
   - Chat assistant available for queries

## Technology Choices

### Why LangGraph?
- Native support for agent orchestration
- State management built-in
- Easy to add conditional logic and error handling
- Integrates well with Langfuse for observability

### Why ReAct Reasoning?
- Allows agents to reason about next steps
- Enables error recovery
- Provides transparency in decision-making
- Supports iterative refinement

### Why Multiple Databases?
- **PostgreSQL**: ACID compliance for critical application data
- **MongoDB**: Flexible schema for varied document structures
- **Redis**: Fast caching for session and temporary data, eligibility assessment caching

### Why Ollama?
- Local model hosting for privacy
- No API costs
- Full control over models
- Primary model: llama3.2 (text model)

## Observability
- Langfuse integration for end-to-end tracing
- Logging at each agent step
- Error tracking and recovery
- Performance monitoring

## Scalability Considerations
- Background task processing (Celery/Redis)
- Database connection pooling
- Caching frequently accessed data
- Horizontal scaling of API servers

