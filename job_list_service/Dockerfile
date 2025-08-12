# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (optional)
EXPOSE 8000

# Default command
CMD ["gunicorn", "job_list_service.wsgi:application", "--bind", "0.0.0.0:8000"]
