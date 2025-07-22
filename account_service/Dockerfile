# Use official Python image as base
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /code

# Copy the requirements.txt first and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your Django project code into the container
COPY . .

# Expose the port Django runs on (for development)
EXPOSE 8000

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
