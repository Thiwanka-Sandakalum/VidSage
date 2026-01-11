
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update --no-install-suggests --no-install-recommends && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

RUN apt-get update --no-install-suggests --no-install-recommends && \
    apt-get install -y --no-install-recommends libpq-dev curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir playwright

COPY --from=builder /usr/local /usr/local
COPY . .


RUN useradd -m appuser && chown -R appuser /app




USER appuser

RUN playwright install chromium

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
