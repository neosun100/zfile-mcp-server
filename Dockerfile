FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn httpx
COPY server.py .

EXPOSE 8092
CMD ["python", "server.py"]
