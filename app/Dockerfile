FROM python:3.12-slim

# OpenShift tends to run containers as random non-root UIDs
# So make sure directories are world-readable/executable
WORKDIR /app

# Install system deps for psycopg2
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Gunicorn entrypoint
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
