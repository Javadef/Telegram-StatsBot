# Python Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create sessions directory and copy existing session files if they exist
RUN mkdir -p /app/sessions && \
    if [ -f telegram_scraper_session.session ]; then \
        cp telegram_scraper_session.session /app/sessions/ 2>/dev/null || true; \
    fi && \
    if [ -f telegram_scraper_session.session-journal ]; then \
        cp telegram_scraper_session.session-journal /app/sessions/ 2>/dev/null || true; \
    fi

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
