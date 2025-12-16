#!/bin/bash

# Setup script for Social Support Application System

echo "Setting up Social Support Application System..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv aisocial
fi

# Activate virtual environment
echo "Activating virtual environment..."
source aisocial/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads
mkdir -p models
mkdir -p logs

# Initialize databases
echo "Initializing databases..."
# Run from project root to ensure imports work
cd "$(dirname "$0")/.." && python3 scripts/init_databases.py

# Check Ollama
echo "Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    echo "Please ensure Ollama is running and models are downloaded:"
    echo "  ollama pull llama3.2"
    echo "  ollama pull llava"
else
    echo "!! Ollama not found. Please install from https://ollama.ai"
fi

# Check Docker
echo "Checking Docker..."
if command -v docker &> /dev/null; then
    echo "✓ Docker is installed"
    echo "Starting databases with Docker Compose..."
    docker-compose up -d
    echo "Waiting for databases to be ready..."
    sleep 10
else
    echo "!! Docker not found. Please install Docker to run databases."
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure settings"
echo "2. Ensure Ollama is running with required models"
echo "3. Start the API: uvicorn api.main:app --reload"
echo "4. Start the frontend: streamlit run frontend/app.py"

