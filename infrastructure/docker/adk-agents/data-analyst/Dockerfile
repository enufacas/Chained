# Data Analyst Agent Dockerfile
# ==============================
# ADK-based A2A agent for data analysis and insights

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (for caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared /app/shared

# Copy agent code
COPY data-analyst /app

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run the agent
CMD ["python", "agent.py"]
