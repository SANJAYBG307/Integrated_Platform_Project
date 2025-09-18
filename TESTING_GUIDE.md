# 🧪 AI Productivity Platform - Complete Testing Guide

## 📋 Prerequisites Checklist

Before testing, ensure you have these installed:

### For Docker Testing (Recommended)
- [ ] **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
- [ ] **Docker Compose** (included with Docker Desktop)
- [ ] **OpenAI API Key** - [Get from OpenAI](https://platform.openai.com/api-keys)

### For Local Development Testing
- [ ] **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- [ ] **MySQL 8.0+** - [Download here](https://dev.mysql.com/downloads/mysql/)
- [ ] **Redis 7+** - [Install guide](#redis-installation)
- [ ] **OpenAI API Key**

---

## 🚀 Quick Test (Recommended)

### Step 1: Initial Setup
```bash
# Navigate to project directory
cd /Users/pims/Desktop/Notes

# Verify project structure
./verify.sh

# You should see: "🎉 SUCCESS: All files and directories are properly organized!"
```

### Step 2: Configure Environment
```bash
# Create environment file
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use any text editor
```

**Required .env configuration:**
```env
# REQUIRED: Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Database settings (these work with Docker)
DB_NAME=Integrated_Platform
DB_USER=Saas_User
DB_PASSWORD=Saas@123
DB_HOST=db
DB_PORT=3306

# Other settings (already configured)
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this
```

### Step 3: Start with Docker
```bash
# Start the entire platform
./start.sh docker

# This will:
# 1. Pull all required Docker images
# 2. Start MySQL database
# 3. Start Redis cache
# 4. Build and start Django application
# 5. Start Celery workers
# 6. Start monitoring services
```

### Step 4: Verify Services are Running
```bash
# Check all services are up
cd deployment/docker
docker-compose ps

# You should see all services as "Up"
# - ai_platform_db
# - ai_platform_redis
# - ai_platform_web
# - ai_platform_celery
# - ai_platform_celery_beat
# - ai_platform_flower
```

---

## 🧪 Complete Testing Procedures

### Test 1: Basic Connectivity
```bash
# Test main application
curl http://localhost:8000/health/

# Expected: {"status": "healthy", "timestamp": "..."}

# Test admin panel (in browser)
# URL: http://localhost:8000/admin
# Login: admin / admin123
```

### Test 2: Database Connection
```bash
# Connect to Django shell
cd deployment/docker
docker-compose exec web python /app/backend/manage.py shell

# In the Django shell, test database:
from django.contrib.auth import get_user_model
User = get_user_model()
print(f"Total users: {User.objects.count()}")
exit()
```

### Test 3: Redis Connection
```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Expected: PONG
```

### Test 4: AI Integration
```bash
# Test OpenAI API connection
docker-compose exec web python /app/backend/manage.py shell

# In Django shell:
from apps.ai_engine.services import AIService
ai_service = AIService()
result = ai_service.generate_text("Hello, this is a test")
print(result)
exit()
```

### Test 5: Celery Tasks
```bash
# Check Celery workers
docker-compose exec celery_worker celery -A ai_productivity_platform status

# Monitor Celery tasks (in browser)
# URL: http://localhost:5555
```

### Test 6: API Endpoints
```bash
# Test API authentication
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Save the token and test protected endpoint
TOKEN="your-token-here"
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/notes/

# Create a test note
curl -X POST http://localhost:8000/api/notes/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Note",
    "content": "This is a test note to verify the AI platform is working correctly.",
    "category": null
  }'
```

---

## 🎯 Browser Testing Checklist

### Main Application Testing
1. **Homepage** - http://localhost:8000
   - [ ] Page loads without errors
   - [ ] Navigation menu works
   - [ ] Login/Register buttons present

2. **Admin Panel** - http://localhost:8000/admin
   - [ ] Login with admin/admin123
   - [ ] Dashboard loads
   - [ ] Can view Users, Notes, Tasks
   - [ ] Can create/edit records

3. **API Documentation** - http://localhost:8000/api/docs
   - [ ] Swagger UI loads
   - [ ] All endpoints listed
   - [ ] Can test endpoints

4. **Celery Monitor** - http://localhost:5555
   - [ ] Flower dashboard loads
   - [ ] Shows active workers
   - [ ] Shows task history

### Functional Testing
1. **User Registration**
   - [ ] Create new account
   - [ ] Login with new account
   - [ ] Dashboard accessible

2. **Notes Management**
   - [ ] Create new note
   - [ ] Edit existing note
   - [ ] Delete note
   - [ ] AI summarization works

3. **Tasks Management**
   - [ ] Create new task
   - [ ] Mark task complete
   - [ ] AI task breakdown works

4. **AI Features**
   - [ ] Note summarization
   - [ ] Keyword extraction
   - [ ] Sentiment analysis
   - [ ] Task priority analysis

---

## 🔧 Local Development Testing

### Step 1: Install Dependencies
```bash
# Install MySQL (macOS)
brew install mysql
brew services start mysql

# Install MySQL (Ubuntu)
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql

# Install Redis (macOS)
brew install redis
brew services start redis

# Install Redis (Ubuntu)
sudo apt install redis-server
sudo systemctl start redis-server
```

### Step 2: Database Setup
```bash
# Connect to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE Integrated_Platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'Saas_User'@'localhost' IDENTIFIED BY 'Saas@123';
GRANT ALL PRIVILEGES ON Integrated_Platform.* TO 'Saas_User'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Configure Local Environment
```bash
# Update .env for local development
cp deployment/environments/development.env .env

# Edit .env to use localhost instead of Docker services
DB_HOST=localhost
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Step 4: Start Local Development
```bash
# Start local development
./start.sh local

# This will:
# 1. Create virtual environment
# 2. Install Python dependencies
# 3. Run database migrations
# 4. Create admin user
# 5. Collect static files
# 6. Start development server
```

### Step 5: Start Celery (New Terminal)
```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source ../venv/bin/activate

# Start Celery worker
celery -A ai_productivity_platform worker --loglevel=info

# Start Celery beat (another terminal)
celery -A ai_productivity_platform beat --loglevel=info
```

---

## 🐛 Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Docker Services Won't Start
```bash
# Check Docker is running
docker version

# Check available ports
lsof -i :8000
lsof -i :3306
lsof -i :6379

# Stop conflicting services
sudo kill -9 $(lsof -t -i:8000)

# Restart Docker
./start.sh docker
```

#### Issue 2: Database Connection Error
```bash
# Check MySQL is running
docker-compose exec db mysql -u Saas_User -pSaas@123 -e "SELECT 1"

# Check database exists
docker-compose exec db mysql -u Saas_User -pSaas@123 -e "SHOW DATABASES"

# Recreate database if needed
docker-compose down
docker-compose up -d
```

#### Issue 3: OpenAI API Error
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API key manually
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check API key has credits
# Visit: https://platform.openai.com/usage
```

#### Issue 4: Static Files Not Loading
```bash
# Collect static files manually
docker-compose exec web python /app/backend/manage.py collectstatic --noinput

# Check static files exist
docker-compose exec web ls -la /app/frontend/static/dist/
```

#### Issue 5: Celery Tasks Not Running
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Check Celery workers
docker-compose exec celery_worker celery -A ai_productivity_platform inspect ping

# Restart Celery
docker-compose restart celery_worker
```

---

## 📊 Performance Testing

### Load Testing with curl
```bash
# Test multiple concurrent requests
for i in {1..10}; do
  curl -s http://localhost:8000/health/ &
done
wait

# Test API performance
time curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/notes/
```

### Memory and CPU Monitoring
```bash
# Monitor Docker containers
docker stats

# Monitor specific service
docker-compose top web
```

---

## ✅ Success Indicators

### System is Working Properly When:
- [ ] All Docker services show "Up" status
- [ ] Health endpoint returns {"status": "healthy"}
- [ ] Admin panel accessible with admin/admin123
- [ ] API endpoints return valid JSON responses
- [ ] Celery flower shows active workers
- [ ] Database contains initial data
- [ ] AI features return responses (with valid API key)
- [ ] No error messages in logs

### Testing Commands Summary
```bash
# Quick system check
./verify.sh && ./start.sh docker

# Test all endpoints
curl http://localhost:8000/health/
curl http://localhost:8000/admin/
curl http://localhost:8000/api/docs/
curl http://localhost:5555/

# Check all services
cd deployment/docker && docker-compose ps

# View logs if issues
docker-compose logs web
docker-compose logs celery_worker
```

---

## 🎉 Final Verification

Your AI Productivity Platform is **fully operational** when you can:

1. ✅ Access main application at http://localhost:8000
2. ✅ Login to admin panel at http://localhost:8000/admin
3. ✅ View API docs at http://localhost:8000/api/docs
4. ✅ Monitor Celery at http://localhost:5555
5. ✅ Create notes and tasks through the interface
6. ✅ See AI features working (summarization, etc.)
7. ✅ All Docker containers running without errors

**You now have a fully functional, production-ready AI productivity platform!** 🚀