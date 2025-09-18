# 🎮 AI Productivity Platform - Complete Operation Manual

## 📖 Table of Contents
1. [Quick Start](#quick-start)
2. [Daily Operations](#daily-operations)
3. [User Management](#user-management)
4. [AI Features Usage](#ai-features-usage)
5. [API Operations](#api-operations)
6. [System Monitoring](#system-monitoring)
7. [Maintenance](#maintenance)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Verify project structure
./verify.sh

# 2. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 3. Start the platform
./start.sh docker

# 4. Access the application
# Main App: http://localhost:8000
# Admin: http://localhost:8000/admin (admin/admin123)
```

### Daily Startup
```bash
# Start all services
./start.sh docker

# Check system status
cd deployment/docker
docker-compose ps
```

### Shutdown
```bash
# Stop all services gracefully
cd deployment/docker
docker-compose down

# Stop and remove volumes (complete cleanup)
docker-compose down -v
```

---

## 🎯 Daily Operations

### Starting Your Work Day
1. **Start the Platform**
   ```bash
   ./start.sh docker
   ```

2. **Verify Everything is Running**
   ```bash
   # Quick health check
   curl http://localhost:8000/health/

   # Check all services
   cd deployment/docker
   docker-compose ps
   ```

3. **Access Your Workspace**
   - Main Application: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - API Docs: http://localhost:8000/api/docs
   - Task Monitor: http://localhost:5555

### During Development
1. **View Logs in Real-time**
   ```bash
   # All services
   docker-compose logs -f

   # Specific service
   docker-compose logs -f web
   docker-compose logs -f celery_worker
   ```

2. **Execute Commands**
   ```bash
   # Django management commands
   docker-compose exec web python /app/backend/manage.py shell
   docker-compose exec web python /app/backend/manage.py createsuperuser
   docker-compose exec web python /app/backend/manage.py migrate

   # Database access
   docker-compose exec db mysql -u Saas_User -pSaas@123 Integrated_Platform

   # Redis access
   docker-compose exec redis redis-cli
   ```

### End of Day
```bash
# Save your work (if needed)
docker-compose exec web python /app/backend/manage.py dumpdata > backup.json

# Stop services (optional - can keep running)
docker-compose stop

# Or full shutdown with cleanup
docker-compose down
```

---

## 👥 User Management

### Admin Operations (via http://localhost:8000/admin)

#### Creating Users
1. Login to admin panel (admin/admin123)
2. Go to "Users" section
3. Click "Add User"
4. Fill in required fields:
   - Username
   - Email
   - Password
   - Full Name
   - User Type (free/premium)

#### Managing User Quotas
```python
# Via Django shell
docker-compose exec web python /app/backend/manage.py shell

from apps.users.models import CustomUser
user = CustomUser.objects.get(username='john')
user.ai_request_quota = 100  # Set monthly quota
user.is_premium = True
user.save()
```

#### Bulk User Operations
```bash
# Export users
docker-compose exec web python /app/backend/manage.py dumpdata users.CustomUser > users_backup.json

# Import users
docker-compose exec web python /app/backend/manage.py loaddata users_backup.json
```

### API User Management
```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Create user via API
TOKEN="your-token-here"
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "New User"
  }'
```

---

## 🤖 AI Features Usage

### Note Summarization
```bash
# Via API
curl -X POST http://localhost:8000/api/notes/1/summarize/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json"

# Response: {"summary": "AI-generated summary..."}
```

### Keyword Extraction
```bash
curl -X POST http://localhost:8000/api/notes/1/extract_keywords/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"count": 5}'

# Response: {"keywords": ["keyword1", "keyword2", ...]}
```

### Task Breakdown
```bash
curl -X POST http://localhost:8000/api/tasks/1/breakdown/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json"

# Response: {"subtasks": ["subtask1", "subtask2", ...]}
```

### Priority Analysis
```bash
curl -X POST http://localhost:8000/api/tasks/1/analyze_priority/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"context": "urgent project deadline"}'

# Response: {"priority": "high", "reasoning": "..."}
```

### Monitoring AI Usage
```bash
# Check usage via admin panel or API
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/users/me/ai_usage/

# Response includes: requests_made, quota_remaining, cost_this_month
```

---

## 📡 API Operations

### Authentication
```bash
# Get token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token for authenticated requests
TOKEN="your-token-here"
curl -H "Authorization: Token $TOKEN" http://localhost:8000/api/notes/
```

### Notes Management
```bash
# List all notes
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/notes/

# Create note
curl -X POST http://localhost:8000/api/notes/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Note",
    "content": "This is my note content",
    "category": 1
  }'

# Update note
curl -X PATCH http://localhost:8000/api/notes/1/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# Delete note
curl -X DELETE http://localhost:8000/api/notes/1/ \
  -H "Authorization: Token $TOKEN"
```

### Tasks Management
```bash
# List tasks
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/tasks/

# Create task
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project",
    "description": "Finish the AI platform",
    "priority": "high",
    "due_date": "2024-12-31"
  }'

# Mark task complete
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_completed": true}'
```

---

## 📊 System Monitoring

### Health Monitoring
```bash
# System health check
curl http://localhost:8000/health/

# Detailed system status (admin only)
curl -H "Authorization: Token $ADMIN_TOKEN" \
  http://localhost:8000/api/core/system/status/
```

### Service Monitoring
```bash
# Check all Docker services
docker-compose ps

# Monitor resource usage
docker stats

# Check specific service health
docker-compose exec web python /app/backend/manage.py check
```

### Celery Monitoring
```bash
# Celery worker status
docker-compose exec celery_worker celery -A ai_productivity_platform status

# Active tasks
docker-compose exec celery_worker celery -A ai_productivity_platform inspect active

# Flower web interface
# Visit: http://localhost:5555
```

### Database Monitoring
```bash
# Database size and status
docker-compose exec db mysql -u Saas_User -pSaas@123 -e "
SELECT
  table_schema as 'Database',
  sum(data_length + index_length) / 1024 / 1024 as 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'Integrated_Platform'
GROUP BY table_schema;"

# Active connections
docker-compose exec db mysql -u Saas_User -pSaas@123 -e "SHOW PROCESSLIST;"
```

### Log Monitoring
```bash
# Real-time application logs
docker-compose logs -f web

# Error logs only
docker-compose logs web 2>&1 | grep ERROR

# Celery task logs
docker-compose logs -f celery_worker

# Database logs
docker-compose logs -f db
```

---

## 🔧 Maintenance

### Daily Maintenance
```bash
# Check system health
./verify.sh

# Clean up Docker resources
docker system prune -f

# Check disk space
df -h
docker system df
```

### Weekly Maintenance
```bash
# Database backup
docker-compose exec db mysqldump -u Saas_User -pSaas@123 Integrated_Platform > backup_$(date +%Y%m%d).sql

# Update application data
docker-compose exec web python /app/backend/manage.py clearsessions
docker-compose exec web python /app/backend/manage.py collectstatic --noinput
```

### Monthly Maintenance
```bash
# Full system backup
docker-compose exec web python /app/backend/manage.py dumpdata > full_backup_$(date +%Y%m%d).json

# Clean old logs
find deployment/docker/logs -name "*.log" -mtime +30 -delete

# Update AI templates and models
docker-compose exec web python /app/backend/manage.py shell -c "
from apps.ai_engine.management.commands.update_ai_models import Command
Command().handle()
"
```

---

## 💾 Backup & Recovery

### Creating Backups
```bash
# Database backup
docker-compose exec db mysqldump -u Saas_User -pSaas@123 Integrated_Platform > db_backup.sql

# Application data backup
docker-compose exec web python /app/backend/manage.py dumpdata > app_backup.json

# Media files backup
docker cp ai_platform_web:/app/media ./media_backup

# Full system backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups/$DATE

# Database
docker-compose exec db mysqldump -u Saas_User -pSaas@123 Integrated_Platform > backups/$DATE/database.sql

# Application data
docker-compose exec web python /app/backend/manage.py dumpdata > backups/$DATE/app_data.json

# Media files
docker cp ai_platform_web:/app/media backups/$DATE/

echo "Backup completed: backups/$DATE"
EOF

chmod +x backup.sh
./backup.sh
```

### Restoring from Backup
```bash
# Restore database
docker-compose exec db mysql -u Saas_User -pSaas@123 Integrated_Platform < db_backup.sql

# Restore application data
docker-compose exec web python /app/backend/manage.py loaddata app_backup.json

# Restore media files
docker cp media_backup ai_platform_web:/app/media
```

### Automated Backups
```bash
# Add to cron for daily backups
crontab -e

# Add this line for daily backup at 2 AM
0 2 * * * /path/to/your/project/backup.sh
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Services Won't Start
```bash
# Check what's using the ports
lsof -i :8000 :3306 :6379 :5555

# Kill conflicting processes
sudo kill -9 $(lsof -t -i:8000)

# Restart Docker
docker-compose down
docker-compose up -d
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec db mysql -u root -proot_password_123 -e "SELECT 1"

# Reset database connection
docker-compose restart db
sleep 10
docker-compose restart web
```

#### AI Features Not Working
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Test API connectivity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check AI service logs
docker-compose logs celery_worker | grep -i openai
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Scale services if needed
docker-compose up -d --scale celery_worker=3

# Check for slow queries
docker-compose exec db mysql -u Saas_User -pSaas@123 -e "
SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST
WHERE COMMAND != 'Sleep' AND TIME > 10;"
```

#### Memory Issues
```bash
# Clean up Docker resources
docker system prune -a -f

# Restart services to free memory
docker-compose restart

# Check Django memory usage
docker-compose exec web python -c "
import psutil
process = psutil.Process()
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

### Emergency Procedures

#### Complete System Reset
```bash
# CAUTION: This will delete all data!
docker-compose down -v
docker system prune -a -f
./start.sh docker
```

#### Recovery from Corruption
```bash
# Stop all services
docker-compose down

# Restore from backup
docker-compose exec db mysql -u Saas_User -pSaas@123 Integrated_Platform < latest_backup.sql

# Restart services
docker-compose up -d

# Verify integrity
./verify.sh
```

---

## 📞 Quick Reference Commands

### Essential Commands
```bash
# Start platform
./start.sh docker

# Stop platform
cd deployment/docker && docker-compose down

# System check
./verify.sh

# View logs
docker-compose logs -f web

# Django shell
docker-compose exec web python /app/backend/manage.py shell

# Database shell
docker-compose exec db mysql -u Saas_User -pSaas@123 Integrated_Platform

# Health check
curl http://localhost:8000/health/
```

### Emergency Commands
```bash
# Force restart
docker-compose restart

# Complete reset (DATA LOSS!)
docker-compose down -v && docker system prune -f && ./start.sh docker

# Get help
./start.sh help
```

---

## ✅ Operation Checklist

### Daily Operations
- [ ] Start platform: `./start.sh docker`
- [ ] Check health: `curl http://localhost:8000/health/`
- [ ] Monitor logs: `docker-compose logs -f web`
- [ ] Verify AI quota usage
- [ ] Check system resources: `docker stats`

### Weekly Operations
- [ ] Create backup: `./backup.sh`
- [ ] Clean Docker resources: `docker system prune -f`
- [ ] Update user quotas if needed
- [ ] Review error logs
- [ ] Test AI features

### Monthly Operations
- [ ] Full system backup
- [ ] Review and clean old data
- [ ] Update AI templates
- [ ] Security review
- [ ] Performance optimization

**Your AI Productivity Platform is now fully operational and ready for production use!** 🎉