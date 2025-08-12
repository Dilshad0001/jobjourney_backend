FROM python:3.11-slim

WORKDIR /code

# Install system dependencies required for psycopg2 and build tools
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install --no-cache-dir -r /code/requirements.txt

# Copy project files
COPY . /code/

ENV PYTHONUNBUFFERED=1

# Start Daphne ASGI server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8003", "message_service.asgi:application"]
