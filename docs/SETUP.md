# Setup Guide

## Prerequisites

1. **Python 3.10+**
   ```bash
   python3 --version
   ```

2. **Docker and Docker Compose**
   - Install from https://www.docker.com/get-started

3. **Ollama**
   - Install from https://ollama.ai
   - Required model: `llama3.2` (text model)
   - Optional: `llava` (vision model for future image processing enhancements)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai_social_support_automation

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional - defaults work for local development)
```

### 3. Start Databases

```bash
# Start all databases with Docker Compose
docker-compose up -d

# Verify databases are running
docker-compose ps
```

### 4. Download Ollama Models

```bash
# Start Ollama service (if not running)
ollama serve

# In another terminal, download required model
ollama pull llama3.2

# Optional: Download vision model for future enhancements
# ollama pull llava
```

### 5. Initialize Databases

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Initialize database schemas
python3 scripts/init_databases.py
```

### 6. Start the Application

**Terminal 1 - Start API:**
```bash
source venv/bin/activate
uvicorn api.main:app --reload
```

**Terminal 2 - Start Frontend:**
```bash
source venv/bin/activate
streamlit run frontend/app.py
```

### 7. Access the Application

- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Manual Setup

If the setup script doesn't work, follow these steps:

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Create Directories

```bash
mkdir -p uploads models logs
```

### 4. Start Databases

```bash
docker-compose up -d
```

### 5. Initialize Databases

```bash
python scripts/init_databases.py
```

## Troubleshooting

### Database Connection Issues

1. **Check if databases are running:**
   ```bash
   docker-compose ps
   ```

2. **Check database logs:**
   ```bash
   docker-compose logs postgres
   docker-compose logs mongodb
   ```

3. **Restart databases:**
   ```bash
   docker-compose restart
   ```

### Ollama Issues

1. **Check if Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Verify models are downloaded:**
   ```bash
   ollama list
   ```

3. **Test model:**
   ```bash
   ollama run llama3.2 "Hello"
   ```

### Port Conflicts

If ports are already in use:

1. **Change ports in docker-compose.yml**
2. **Update .env file with new ports**
3. **Update API_BASE_URL in frontend/app.py**

### Import Errors

If you see import errors:

1. **Ensure virtual environment is activated**
2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

## Development Mode

For development with hot reload:

```bash
# API with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Streamlit with auto-reload (default)
streamlit run frontend/app.py --server.runOnSave true
```

## Production Deployment

For production:

1. **Use production-grade WSGI server:**
   ```bash
   gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
2. **Configure reverse proxy (Nginx)**
3. **Set up SSL certificates**
4. **Configure proper database backups**
5. **Set up monitoring and logging**

## Testing

Run tests (when available):

```bash
pytest tests/
```

## Next Steps

1. Review the architecture documentation: `docs/ARCHITECTURE.md`
2. Understand agent design: `docs/AGENT_DESIGN.md`
3. Explore the API: http://localhost:8000/docs
4. Try submitting a test application via the frontend

