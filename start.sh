#!/bin/bash

echo "🚀 Applying migrations..."
alembic upgrade head

echo "✅ Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}