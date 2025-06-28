# VidSage Docker Quick Start Script for Windows PowerShell

Write-Host "🚀 VidSage Docker Quick Start" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  No .env file found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please edit .env file with your Google API key before continuing." -ForegroundColor Yellow
    Write-Host "   Edit the .env file and set GOOGLE_API_KEY=your_api_key" -ForegroundColor Yellow
    Read-Host "Press Enter after setting up your API key"
}

# Build the Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Blue
docker build -t vidsage-api:latest .

# Check if container is already running
$existingContainer = docker ps -q -f name=vidsage-api
if ($existingContainer) {
    Write-Host "🔄 Stopping existing container..." -ForegroundColor Yellow
    docker stop vidsage-api
    docker rm vidsage-api
}

# Create data directory
New-Item -ItemType Directory -Force -Path "data\audio", "data\video", "data\subtitles", "data\thumbnails", "data\info", "data\transcripts", "data\summaries", "data\embeddings" | Out-Null

# Get current directory for volume mounting
$currentDir = (Get-Location).Path

# Run the container
Write-Host "🚀 Starting VidSage API container..." -ForegroundColor Green
docker run -d `
    --name vidsage-api `
    -p 8000:8000 `
    --env-file .env `
    -v "${currentDir}\data:/app/data" `
    vidsage-api:latest

# Wait for container to start
Write-Host "⏳ Waiting for API to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ VidSage API is running successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 API URL: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host "🏥 Health Check: http://localhost:8000/health" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📋 Container logs: docker logs -f vidsage-api" -ForegroundColor Gray
        Write-Host "🛑 Stop container: docker stop vidsage-api" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ API failed to start. Check logs:" -ForegroundColor Red
    docker logs vidsage-api
    exit 1
}
