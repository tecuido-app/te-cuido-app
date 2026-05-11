FROM python:3.11-slim

WORKDIR /app

COPY agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent source into agent/ so "from agent.X import Y" resolves correctly
COPY agent/ ./agent/

EXPOSE 8000

# $PORT is injected by Railway/Render; falls back to 8000 for local Docker
CMD ["sh", "-c", "uvicorn agent.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
