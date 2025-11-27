# ADK API Server Dockerfile
# ==========================
# API server for google/adk-web, bridging to A2A protocol agents

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (for caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY __init__.py /app/__init__.py
COPY session_store.py /app/session_store.py
COPY a2a_adapter.py /app/a2a_adapter.py
COPY server.py /app/server.py

# Set environment variables
ENV PORT=8080
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run the server
CMD ["python", "server.py"]
