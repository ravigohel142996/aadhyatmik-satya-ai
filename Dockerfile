FROM node:22-alpine AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend /app/backend
COPY book_chunks.json /app/book_chunks.json
COPY --from=web /web/dist /app/frontend/dist
ENV PYTHONPATH=/app/backend \
    BOOK_CHUNKS_PATH=/app/book_chunks.json \
    FRONTEND_DIST=/app/frontend/dist \
    PYTHONUNBUFFERED=1
WORKDIR /app/backend
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
