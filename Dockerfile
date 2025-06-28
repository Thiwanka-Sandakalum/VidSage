# VidSage API Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the existing virtual environment
COPY myenv/ ./myenv/

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data/{audio,video,subtitles,thumbnails,info,transcripts,summaries,embeddings,vectorstores}

# Create non-root user for security
RUN useradd -m -u 1000 vidsage && \
    chown -R vidsage:vidsage /app
USER vidsage

# Set up Python path to use the virtual environment
ENV PATH="/app/myenv/Scripts:$PATH"
ENV PYTHONPATH="/app/myenv/Lib/site-packages:$PYTHONPATH"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command - use Python from virtual environment
CMD ["/app/myenv/Scripts/python.exe", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
