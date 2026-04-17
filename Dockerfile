# Use the official Python image as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the application code into the container
COPY . .

# Expose the port that Gunicorn will listen on
EXPOSE 8080

ENV PYTHONUNBUFFERED=TRUE

# Command to run the application using Gunicorn
CMD gunicorn --bind 0.0.0.0:8080 app:app --enable-stdio-inheritance --timeout 3600 --workers=2
