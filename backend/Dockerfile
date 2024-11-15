# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed system dependencies (e.g., Chromium and its driver)
RUN apt-get update && apt-get install -y \
    chromium-driver \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-prod.txt

# Download NLTK data during the build phase
RUN python -m nltk.downloader stopwords punkt wordnet \
    && mkdir -p /root/nltk_data

# Expose the Flask app on port 5000
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Install Gunicorn
RUN pip install gunicorn

# Run the application
CMD ["sh", "-c", "gunicorn --workers 3 --threads 4 --bind 0.0.0.0:$PORT app:app"]
