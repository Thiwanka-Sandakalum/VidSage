.PHONY: help build up down restart logs clean test health

# Default target
help:
	@echo "VidSage Microservices - Docker Management"
	@echo ""
	@echo "Available commands:"
	@echo "  make build      - Build all Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - View logs (all services)"
	@echo "  make logs-f     - Follow logs (all services)"
	@echo "  make clean      - Remove containers, volumes, and images"
	@echo "  make health     - Check health of all services"
	@echo "  make test       - Run integration tests"
	@echo "  make test-unit  - Run all unit tests"
	@echo "  make test-transcript - Run transcript service unit tests"
	@echo "  make scale      - Scale workers (usage: make scale WORKERS=3)"
	@echo ""
	@echo "Service-specific commands:"
	@echo "  make logs-gateway       - View gateway logs"
	@echo "  make logs-transcript    - View transcript logs"
	@echo "  make logs-embedding     - View embedding logs"
	@echo "  make logs-generation    - View generation logs"
	@echo "  make rebuild-gateway    - Rebuild gateway service"

# Build all images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Start all services
up:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "✅ Services started! Check health with 'make health'"

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	docker-compose down

# Restart all services
restart: down up

# View logs (all services)
logs:
	docker-compose logs

# Follow logs (all services)
logs-f:
	docker-compose logs -f

# Service-specific logs
logs-gateway:
	docker-compose logs -f gateway-api gateway-worker

logs-transcript:
	docker-compose logs -f transcript-service transcript-worker

logs-embedding:
	docker-compose logs -f embedding-service embedding-worker

logs-generation:
	docker-compose logs -f generation-service

logs-redis:
	docker-compose logs -f redis

# Clean up everything
clean:
	@echo "🧹 Cleaning up containers, volumes, and images..."
	docker-compose down -v --rmi all
	@echo "✅ Cleanup complete!"

# Health checks
health:
	@echo "🏥 Checking service health..."
	@echo "\nGateway API:"
	@curl -s http://localhost:8000/health | jq || echo "❌ Not responding"
	@echo "\nTranscript Service:"
	@curl -s http://localhost:8001/health | jq || echo "❌ Not responding"
	@echo "\nEmbedding Service:"
	@curl -s http://localhost:8002/health | jq || echo "❌ Not responding"
	@echo "\nGeneration Service:"
	@curl -s http://localhost:8003/health | jq || echo "❌ Not responding"

# Scale workers
WORKERS ?= 2
scale:
	@echo "⚖️  Scaling workers to $(WORKERS) instances..."
	docker-compose up -d --scale transcript-worker=$(WORKERS) --scale embedding-worker=$(WORKERS)

# Rebuild specific service
rebuild-gateway:
	docker-compose build gateway-api
	docker-compose up -d gateway-api gateway-worker

rebuild-transcript:
	docker-compose build transcript-service
	docker-compose up -d transcript-service transcript-worker

rebuild-embedding:
	docker-compose build embedding-service
	docker-compose up -d embedding-service embedding-worker

rebuild-generation:
	docker-compose build generation-service
	docker-compose up -d generation-service

# Integration test
test:
	@echo "🧪 Running integration tests..."
	@echo "Testing video submission..."
	@curl -X POST http://localhost:8000/api/v1/videos/process \
		-H "Content-Type: application/json" \
		-d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","user_id":"test_user"}' \
		| jq
	@echo "\n✅ Test complete! Check logs for processing status."

# Unit tests
test-unit:
	@echo "🧪 Running all unit tests..."
	@cd transcript-service && python3 test_mocked.py
	@echo "✅ All unit tests completed!"

test-transcript:
	@echo "🧪 Running transcript service unit tests..."
	@cd transcript-service && python3 test_mocked.py

# Show running containers
ps:
	docker-compose ps

# Shell into service
shell-gateway:
	docker-compose exec gateway-api /bin/bash

shell-transcript:
	docker-compose exec transcript-service /bin/bash

shell-embedding:
	docker-compose exec embedding-service /bin/bash

shell-generation:
	docker-compose exec generation-service /bin/bash

shell-redis:
	docker-compose exec redis redis-cli

# View Redis stream
redis-stream:
	docker-compose exec redis redis-cli XRANGE vidsage:events - + COUNT 10
