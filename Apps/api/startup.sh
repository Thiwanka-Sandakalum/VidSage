#!/bin/bash

# Azure App Service startup script for VidSage API

echo "Starting VidSage API..."

# Install dependencies if not already installed
if [ ! -d "antenv" ]; then
    echo "Creating virtual environment..."
    python -m venv antenv
    source antenv/bin/activate
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source antenv/bin/activate
fi

# Start the application with gunicorn
echo "Starting Gunicorn server..."
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 600 --access-logfile - --error-logfile -
