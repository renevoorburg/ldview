FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories and set permissions
RUN mkdir -p /var/log/ldview && \
    mkdir -p /var/run/ldview && \
    mkdir -p /tmp && \
    touch /var/log/ldview/access.log && \
    touch /var/log/ldview/error.log && \
    chmod -R 777 /var/log/ldview && \
    chmod -R 777 /var/run/ldview && \
    chmod -R 755 /app && \
    chmod -R 777 /tmp

# Switch to non-root user
USER nobody

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
