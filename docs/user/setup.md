# 🚀 AI Productivity Platform Setup Guide

This comprehensive guide will help you set up the AI Productivity Platform in both development and production environments.

## 📋 Prerequisites

### System Requirements
- **Python 3.11+** (for local development)
- **Docker & Docker Compose** (recommended for all environments)
- **MySQL 8.0+** (if not using Docker)
- **Redis 7+** (if not using Docker)
- **OpenAI API Key** (required for AI features)

### Development Tools (Recommended)
- **VS Code** with recommended extensions
- **Git** for version control
- **Postman** or similar for API testing

## 🏃‍♂️ Quick Start (Docker - Recommended)

### 1. Clone and Configure
```bash
# Clone the repository
git clone <your-repository-url>
cd ai-productivity-platform

# Copy environment file
cp deployment/environments/development.env .env
```

### 2. Set Environment Variables
Edit `.env` file with your configuration:
```env
# Required - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key-here

# Database (already configured for Docker)
DB_NAME=Integrated_Platform
DB_USER=Saas_User
DB_PASSWORD=Saas@123
DB_HOST=db
DB_PORT=3306

# Security (change in production)
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Redis (already configured for Docker)
REDIS_URL=redis://:redis_password_123@redis:6379/0
CELERY_BROKER_URL=redis://:redis_password_123@redis:6379/0
CELERY_RESULT_BACKEND=redis://:redis_password_123@redis:6379/0
```

### 3. Start the Platform
```bash
# Navigate to deployment directory
cd deployment/docker

# Start all services (first time)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

### 4. Access the Platform
- **Main Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin (admin/admin123)
- **Celery Monitor**: http://localhost:5555
- **API Docs**: http://localhost:8000/api/docs

### 5. Create Your First User
1. Go to http://localhost:8000
2. Click "Register"
3. Fill in your details
4. Start using AI features!

## 💻 Local Development Setup

### 1. Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```sql
-- Connect to MySQL as root
mysql -u root -p

-- Create database and user
CREATE DATABASE Integrated_Platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'Saas_User'@'localhost' IDENTIFIED BY 'Saas@123';
GRANT ALL PRIVILEGES ON Integrated_Platform.* TO 'Saas_User'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Redis Setup
```bash
# Install Redis (macOS)
brew install redis
brew services start redis

# Install Redis (Ubuntu)
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server

# Install Redis (Windows)
# Download from https://redis.io/download
```

### 4. Django Setup
```bash
# Navigate to backend directory
cd backend

# Set environment variables
export DJANGO_SETTINGS_MODULE=ai_productivity_platform.settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Start development server
python manage.py runserver
```

### 5. Start Celery (New Terminal)
```bash
# Navigate to backend directory
cd backend

# Start Celery worker
celery -A ai_productivity_platform worker --loglevel=info

# Start Celery beat (new terminal)
celery -A ai_productivity_platform beat --loglevel=info

# Optional: Start Flower for monitoring
celery -A ai_productivity_platform flower
```

## 🔧 Configuration Options

### AI Settings
```python
# In .env file
OPENAI_API_KEY=your-api-key-here
AI_MODEL=gpt-3.5-turbo  # or gpt-4
AI_MAX_TOKENS=150
AI_TEMPERATURE=0.7
```

### Database Settings
```python
# In .env file
DB_NAME=Integrated_Platform
DB_USER=Saas_User
DB_PASSWORD=Saas@123
DB_HOST=localhost  # or 'db' for Docker
DB_PORT=3306
```

### Redis/Celery Settings
```python
# In .env file
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 🧪 Testing

### Run Tests
```bash
# Navigate to backend directory
cd backend

# Django tests
python manage.py test

# Pytest (if installed)
pytest

# With coverage
pytest --cov=apps

# Test specific app
python manage.py test apps.notes
```

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health/

# Test API with token
curl -H "Authorization: Token your-token" \
     http://localhost:8000/api/notes/
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u Saas_User -p Integrated_Platform

# Reset password if needed
ALTER USER 'Saas_User'@'localhost' IDENTIFIED BY 'Saas@123';
```

#### 2. Redis Connection Error
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Start Redis if not running
redis-server
```

#### 3. Celery Not Working
```bash
# Check Redis connection
python -c "import redis; r=redis.Redis(); print(r.ping())"

# Check Celery can connect
cd backend
celery -A ai_productivity_platform inspect ping
```

#### 4. AI Features Not Working
- Verify OpenAI API key is correct
- Check API key has sufficient credits
- Check network connectivity to OpenAI API
- Review logs for specific error messages

#### 5. Static Files Missing
```bash
# Collect static files
cd backend
python manage.py collectstatic --noinput

# Check STATIC_ROOT permissions
ls -la ../frontend/static/dist/
```

#### 6. Docker Issues
```bash
# Navigate to deployment directory
cd deployment/docker

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check container logs
docker-compose logs web
docker-compose logs celery_worker
docker-compose logs db
```

### Log Locations
- **Django logs**: `monitoring/logs/ai_platform.log`
- **Celery logs**: `monitoring/logs/celery.log`
- **Docker logs**: `docker-compose logs <service>`
- **System logs**: `/var/log/` (Linux/macOS)

## 🚀 Production Deployment

### Environment Variables
```env
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (use environment-specific values)
DB_PASSWORD=secure-production-password

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

### Docker Production
```bash
# Use production environment
cp deployment/environments/production.env .env

# Navigate to deployment directory
cd deployment/docker

# Start with production settings
docker-compose -f docker-compose.yml up -d
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set production environment
export DJANGO_SETTINGS_MODULE=ai_productivity_platform.settings
export DEBUG=False

# Navigate to backend
cd backend

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start with Gunicorn
gunicorn ai_productivity_platform.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120
```

## 📊 Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:8000/health/

# Database health
cd backend
python manage.py dbshell

# Redis health
redis-cli ping

# Celery health
cd backend
celery -A ai_productivity_platform inspect ping
```

### Performance Monitoring
- Monitor AI API usage and costs
- Track response times
- Monitor database performance
- Watch Redis memory usage
- Monitor Celery queue lengths

### Log Monitoring
```bash
# Real-time logs
tail -f monitoring/logs/ai_platform.log
tail -f monitoring/logs/celery.log

# Docker logs
cd deployment/docker
docker-compose logs -f web
```

## 🔐 Security Checklist

### Before Going Live
- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Enable HTTPS
- [ ] Set up proper firewall rules
- [ ] Review API rate limits
- [ ] Configure proper CORS settings
- [ ] Set up SSL certificates
- [ ] Enable security headers

## 📞 Getting Help

### Documentation
- **API Docs**: http://localhost:8000/api/docs
- **Admin Interface**: http://localhost:8000/admin
- **Django Docs**: https://docs.djangoproject.com/
- **Celery Docs**: https://docs.celeryproject.org/
- **OpenAI Docs**: https://platform.openai.com/docs

### Support
- Check logs for error messages
- Review this setup guide
- Test with minimal configuration
- Search for similar issues online
- Create detailed bug reports with logs

### Development Tools
```bash
# Navigate to backend directory
cd backend

# Django shell for debugging
python manage.py shell

# Database shell
python manage.py dbshell

# Check configuration
python manage.py check

# Show migrations
python manage.py showmigrations
```

## 🎉 Next Steps

Once you have the platform running:

1. **Explore the Interface**: Create notes and tasks
2. **Test AI Features**: Try summarization and analysis
3. **Configure Settings**: Adjust AI models and quotas
4. **Set Up Monitoring**: Configure logging and alerts
5. **Customize**: Modify templates and add features
6. **Scale**: Add more workers and optimize performance

Happy coding! 🎉