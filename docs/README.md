# AI Social Support Application Workflow Automation

## Overview
This project automates the social security department's application process, reducing processing time from 5-20 working days to minutes through AI-powered workflow automation.

## Features
- **Multimodal Data Processing**: Handles text, images, and tabular data from various document types
- **AI Agents**: Orchestrated agents for data extraction, validation, eligibility assessment, and decision recommendation
- **Interactive Chat**: GenAI chatbot for real-time application assistance
- **Local Model Hosting**: Uses Ollama for local LLM inference
- **End-to-End Observability**: Langfuse integration for monitoring and debugging

## Architecture

### Components
1. **Master Orchestrator**: Coordinates all agents and workflow steps
2. **Data Extraction Agent**: Extracts information from documents (PDFs, images, Excel)
3. **Data Validation Agent**: Validates and cross-checks extracted data
4. **Eligibility Check Agent**: Assesses eligibility based on criteria
5. **Decision Recommendation Agent**: Provides final recommendations

### Technology Stack
- **Backend**: Python, FastAPI
- **Databases**: PostgreSQL, MongoDB, Redis
- **ML/LLM**: Scikit-learn, Ollama (local LLMs)
- **Agent Framework**: LangGraph with ReAct reasoning
- **Frontend**: Streamlit
- **Observability**: Langfuse

## Setup Instructions

### Prerequisites
- Python 3.10+
- Docker (for databases)
- Ollama installed and running

### Installation

1. Clone the repository:
```bash
git clone (https://github.com/Kompalk/ai_social_support_automation.git)
cd ai_social_support_automation
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up databases (using Docker):
```bash
docker-compose up -d
```

5. Initialize databases:
```bash
python scripts/init_databases.py
```

6. Download and start Ollama models:
```bash
ollama pull llama3.2

# Optional: Download vision model for future enhancements
# ollama pull llava
```

7. Set environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

8. Run the application:
```bash
# Start FastAPI backend
uvicorn api.main:app --reload

# In another terminal, start Streamlit frontend
streamlit run frontend/app.py
```

## Project Structure
```
ai_social_support_automation/
├── agents/              # AI agent implementations
├── data_processing/     # Data ingestion and processing
├── models/              # ML models and training
├── api/                 # FastAPI backend
├── frontend/            # Streamlit frontend
├── database/            # Database schemas and connections
├── config/              # Configuration files
├── scripts/             # Utility scripts
└── tests/               # Unit tests
```

## Usage

### Submitting an Application
1. Access the Streamlit interface at `http://localhost:8501`
2. Upload required documents:
   - Application form
   - Bank statement
   - Emirates ID
   - Resume
   - Assets/Liabilities Excel file
   - Credit report
3. Interact with the chatbot to complete the application
4. Receive automated eligibility assessment and recommendations

### API Endpoints
- `POST /api/v1/application/submit`: Submit new application
- `GET /api/v1/application/{application_id}`: Get application status
- `POST /api/v1/chat`: Chat with GenAI assistant
- `GET /api/v1/health`: Health check

## Documentation
See `docs/` directory for detailed documentation on:
- Agent architecture
- Data processing pipeline
- Model training and evaluation
- API reference

