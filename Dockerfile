FROM python:3.11-slim

LABEL maintainer="neosun100"
LABEL description="ZFile MCP Server - AI assistant integration for ZFile"
LABEL version="1.0.0"

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn httpx

# Copy server code
COPY server.py .

# Create data directory for token persistence
RUN mkdir -p /data

# Environment variables (to be set at runtime)
ENV ZFILE_URL=""
ENV ZFILE_USER=""
ENV ZFILE_PASS=""
ENV ZFILE_STORAGE_KEY="1"
ENV ACCESS_TOKEN=""

EXPOSE 8092

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8092/health || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8092"]
