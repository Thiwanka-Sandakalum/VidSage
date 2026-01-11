
# ---- Build stage ----
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update --no-install-suggests --no-install-recommends && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Production image ----
FROM python:3.11-slim
WORKDIR /app

# Install runtime dependencies only (if any)
RUN apt-get update --no-install-suggests --no-install-recommends && \
    apt-get install -y --no-install-recommends libpq-dev curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Playwright and browsers
RUN pip install --no-cache-dir playwright && \
    playwright install --with-deps chromium


# Copy installed Python packages and binaries from builder
COPY --from=builder /usr/local /usr/local

# Copy app source
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
