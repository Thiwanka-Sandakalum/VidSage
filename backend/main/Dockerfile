
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
    apt-get install -y --no-install-recommends \
        libpq-dev \
        curl \
        libglib2.0-0 \
        libnss3 \
        libgdk-pixbuf2.0-0 \
        libgtk-3-0 \
        libasound2 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libgbm1 \
        libpango-1.0-0 \
        libcairo2 \
        libatspi2.0-0 \
        libdrm2 \
        libxfixes3 \
        libxext6 \
        libxshmfence1 \
        libxrender1 \
        libx11-6 \
        libxtst6 \
        libpci3 \
        libwayland-client0 \
        libwayland-cursor0 \
        libwayland-egl1 \
        libcups2 \
        libxkbcommon0 \
        libxss1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir playwright

COPY --from=builder /usr/local /usr/local
COPY . .


RUN useradd -m appuser && chown -R appuser /app




USER appuser

RUN playwright install chromium

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
