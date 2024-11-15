# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask app on port 5000
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Install Gunicorn
RUN pip install gunicorn

# Run the application
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:$PORT", "app:app"]

