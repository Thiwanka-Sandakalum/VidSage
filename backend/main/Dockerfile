FROM python:3.11-slim

WORKDIR /app

RUN apt-get update --no-install-suggests --no-install-recommends --no-cache && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update --no-install-suggests --no-install-recommends && \
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
