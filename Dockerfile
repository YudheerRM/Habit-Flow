# Use an official Python runtime as a parent image
FROM python:3.13.0

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by Django and PostgreSQL (optional for future setups)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose the port the app runs on (default Django port)
EXPOSE 8000

# Command to run the app (Django development server)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
