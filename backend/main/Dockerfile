
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
        libnss3 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libgbm1 \
        libgtk-3-0 \
        libnspr4 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        xdg-utils \
        libasound2 \
        libxshmfence1 \
        libxss1 \
        libxtst6 \
        fonts-liberation \
        libappindicator3-1 \
        libatspi2.0-0 \
        libcurl4 \
        libwayland-client0 \
        libwayland-cursor0 \
        libwayland-egl1 \
        libxkbcommon0 \
        libpango-1.0-0 \
        libxrender1 \
        libxext6 \
        libxfixes3 \
        libpci3 \
        libgdk-pixbuf2.0-0 \
        libglib2.0-0 \
        libcairo2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir playwright

COPY --from=builder /usr/local /usr/local
COPY . .


RUN useradd -m appuser && chown -R appuser /app




USER appuser

RUN playwright install chromium

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
