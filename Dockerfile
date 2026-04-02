FROM python:3.11-slim

# Prevent .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install dependencies (cached layer — only re-runs if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create instance directory for SQLite (Fly volume will be mounted here in production)
RUN mkdir -p instance

EXPOSE 8080

# 2 workers is appropriate for 512 MB RAM; increase if you upgrade your VM
# --preload initialises the app once in the master process before workers fork,
# preventing multiple workers from racing to create the database tables.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "--preload", "--access-logfile", "-", "wsgi:app"]
