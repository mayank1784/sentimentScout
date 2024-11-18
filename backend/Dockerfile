# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed system dependencies (e.g., Chromium and its driver)
RUN apt-get update && apt-get install -y --no-install-recommends\
    chromium-driver \
    build-essential \
    chromium \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libgbm1 \
    libxdamage1 \
    libasound2 \
    libxshmfence1 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libatk1.0-0 \
    && apt-get clean \
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
CMD ["sh", "-c", "gunicorn --workers 3 --threads 4 --bind 0.0.0.0:$PORT"]
