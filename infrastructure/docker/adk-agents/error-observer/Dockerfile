# Use Python 3.11 slim image
FROM python:3.11-slim

WORKDIR /app

# Copy shared utilities
COPY shared/ /app/shared/

# Copy agent code
COPY error-observer/ /app/error-observer/

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn[standard]>=0.23.0 \
    httpx>=0.24.0 \
    pydantic>=2.0.0

# Expose port
EXPOSE 8090

# Run the agent
CMD ["python", "-m", "error-observer.agent"]
