FROM python:3.11-slim

LABEL maintainer="neosun100"
LABEL description="ZFile MCP Server - AI assistant integration for ZFile"
LABEL version="1.3.2"

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn httpx python-multipart

COPY server.py .

RUN mkdir -p /data /tmp/zfile-chunks

ENV ZFILE_URL=""
ENV ZFILE_USER=""
ENV ZFILE_PASS=""
ENV ZFILE_STORAGE_KEY="1"
ENV ACCESS_TOKEN=""
ENV CHUNK_SIZE_MB="10"
ENV MCP_SERVER_URL=""

EXPOSE 8092

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8092/health', timeout=5).raise_for_status()" || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8092"]
