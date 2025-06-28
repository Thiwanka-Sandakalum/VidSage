#!/bin/bash

# VidSage Docker Quick Start Script

set -e

echo "🚀 VidSage Docker Quick Start"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your Google API key before continuing."
    echo "   Run: nano .env"
    read -p "Press Enter after setting up your API key..."
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t vidsage-api:latest .

# Check if container is already running
if docker ps -q -f name=vidsage-api > /dev/null; then
    echo "🔄 Stopping existing container..."
    docker stop vidsage-api
    docker rm vidsage-api
fi

# Create data directory
mkdir -p data/{audio,video,subtitles,thumbnails,info,transcripts,summaries,embeddings}

# Run the container
echo "🚀 Starting VidSage API container..."
docker run -d \
    --name vidsage-api \
    -p 8000:8000 \
    --env-file .env \
    -v $(pwd)/data:/app/data \
    vidsage-api:latest

# Wait for container to start
echo "⏳ Waiting for API to start..."
sleep 5

# Check health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ VidSage API is running successfully!"
    echo ""
    echo "🌐 API URL: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo "🏥 Health Check: http://localhost:8000/health"
    echo ""
    echo "📋 Container logs: docker logs -f vidsage-api"
    echo "🛑 Stop container: docker stop vidsage-api"
else
    echo "❌ API failed to start. Check logs:"
    docker logs vidsage-api
    exit 1
fi
