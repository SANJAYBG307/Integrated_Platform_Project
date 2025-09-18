# AI Productivity Platform Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-mysql-client \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev \
        curl \
        wget \
        git \
        nginx \
        supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install Python dependencies
COPY ../../requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY ../../backend /app/backend
COPY ../../frontend /app/frontend
COPY ../../database /app/database
COPY ../../requirements.txt /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs /var/log/supervisor

# Set permissions
RUN chown -R appuser:appuser /app
RUN chmod +x /app/deployment/scripts/docker-entrypoint.sh

# Copy configuration files
COPY ../../deployment/docker/nginx/nginx.conf /etc/nginx/sites-available/default
COPY ../../deployment/docker/supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set working directory to backend and collect static files
WORKDIR /app/backend
RUN python manage.py collectstatic --noinput
WORKDIR /app

# Expose ports
EXPOSE 8000 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Switch to non-root user
USER appuser

# Run the application
CMD ["/app/deployment/scripts/docker-entrypoint.sh"]