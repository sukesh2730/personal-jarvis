# JARVIS Docker Container
# Production-ready container for ROME JARVIS AI Assistant

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    portaudio19-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs logs/notes logs/summaries sounds sounds/tts_cache templates

# Expose ports
EXPOSE 5000 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=dashboard.py
ENV FASTAPI_APP=api_server.py

# Default command (can be overridden)
CMD ["python", "main.py"]
