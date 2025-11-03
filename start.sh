#!/bin/bash
# Quick start script for Daedalus Agent

echo "🚀 Starting Daedalus Agent..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Please create .env from .env.example and configure your credentials."
    exit 1
fi

# Start Chainlit
echo "Starting Chainlit on http://localhost:8000"
chainlit run daedalus.py -w
