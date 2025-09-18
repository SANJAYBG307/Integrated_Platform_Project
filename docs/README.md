# 🧠 AI Productivity Platform

A comprehensive, production-ready AI-integrated productivity platform built with Django, featuring intelligent note-taking, smart task management, and AI-powered insights.

## 🌟 Features

### 🤖 AI-Powered Intelligence
- **Smart Summarization**: Automatic note summarization with configurable length
- **Keyword Extraction**: AI-powered keyword identification
- **Sentiment Analysis**: Emotional tone analysis of content
- **Task Breakdown**: Intelligent task decomposition into subtasks
- **Priority Analysis**: AI-suggested task prioritization
- **Time Estimation**: Automated time estimation for tasks
- **Productivity Insights**: Personalized productivity analytics

### 📝 Note Management
- **Rich Text Notes**: Create, edit, and organize notes with categories and tags
- **AI Processing**: Automatic AI analysis of note content
- **Version History**: Track changes and restore previous versions
- **Smart Search**: AI-enhanced search across all notes
- **Sharing**: Share notes with other users or publicly

### ✅ Task Management
- **Smart Tasks**: Create tasks with AI-powered suggestions
- **Subtask Management**: Break down complex tasks automatically
- **Priority System**: AI-suggested and manual priority setting
- **Due Date Tracking**: Never miss a deadline
- **Progress Monitoring**: Track task completion and productivity

### 👤 User Experience
- **Personalized Dashboard**: AI-driven insights and quick actions
- **Real-time Notifications**: Stay updated with important events
- **Usage Analytics**: Monitor AI usage and productivity metrics
- **Mobile Responsive**: Works seamlessly on all devices

### 🔒 Enterprise Features
- **Rate Limiting**: Prevent API abuse with configurable limits
- **Usage Quotas**: Manage AI costs with user quotas
- **Security**: Enterprise-grade security with proper authentication
- **Monitoring**: Comprehensive logging and health checks
- **Scalability**: Built for high-performance production deployment

## 🏗️ Architecture

### Backend Stack
- **Django 4.2**: Modern Python web framework
- **Django REST Framework**: API development
- **MySQL 8.0**: Robust relational database
- **Redis**: Caching and message broker
- **Celery**: Asynchronous task processing

### AI Integration
- **OpenAI GPT Models**: GPT-3.5 Turbo and GPT-4 support
- **Configurable Templates**: Customizable AI prompts
- **Cost Management**: Token usage tracking and quotas
- **Error Handling**: Robust error handling and retries

### Frontend
- **Bootstrap 5**: Modern, responsive UI framework
- **JavaScript ES6+**: Interactive user experience
- **Progressive Enhancement**: Works without JavaScript
- **Responsive Design**: Mobile-first approach

### DevOps & Deployment
- **Docker**: Containerized deployment
- **Docker Compose**: Multi-service orchestration
- **Nginx**: Reverse proxy and static file serving
- **Supervisor**: Process management
- **Health Checks**: Comprehensive monitoring

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- MySQL database access

### 1. Clone and Setup
```bash
git clone <repository-url>
cd ai-productivity-platform
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file with your settings:
```env
OPENAI_API_KEY=your-openai-api-key-here
DB_PASSWORD=Saas@123
SECRET_KEY=your-super-secret-key
```

### 3. Start with Docker
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

### 4. Access the Platform
- **Main Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/docs
- **Celery Monitoring**: http://localhost:5555

### Default Credentials
- **Admin User**: admin / admin123
- **Database**: Saas_User / Saas@123

## 💻 Development Setup

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Database Setup
```sql
CREATE DATABASE Integrated_Platform;
CREATE USER 'Saas_User'@'localhost' IDENTIFIED BY 'Saas@123';
GRANT ALL PRIVILEGES ON Integrated_Platform.* TO 'Saas_User'@'localhost';
```

### Celery Workers
```bash
# Start Celery worker
celery -A ai_productivity_platform worker --loglevel=info

# Start Celery beat (scheduler)
celery -A ai_productivity_platform beat --loglevel=info

# Monitor with Flower
celery -A ai_productivity_platform flower
```

## 📚 API Documentation

### Authentication
```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
curl -H "Authorization: Token your-token-here" \
  http://localhost:8000/api/notes/
```

### AI Analysis
```bash
# Analyze text with AI
curl -X POST http://localhost:8000/api/ai/analyze/text/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here", "type": "summarize"}'
```

### Notes Management
```bash
# Create note
curl -X POST http://localhost:8000/api/notes/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Note", "content": "Note content"}'

# Get notes
curl -H "Authorization: Token your-token" \
  http://localhost:8000/api/notes/
```

## 🔧 Configuration

### AI Settings
Configure AI behavior in `settings.py`:
```python
OPENAI_API_KEY = 'your-api-key'
AI_MODEL = 'gpt-3.5-turbo'
AI_MAX_TOKENS = 150
AI_TEMPERATURE = 0.7
```

### Rate Limiting
Configure rate limits in Django admin:
- Endpoint patterns
- Request limits per time window
- User type restrictions

### Usage Quotas
Set AI usage quotas for users:
- Monthly request limits
- Token usage limits
- Automatic reset schedules

## 📊 Monitoring

### Health Checks
```bash
# Check application health
curl http://localhost:8000/health/

# Check system status (admin required)
curl -H "Authorization: Token admin-token" \
  http://localhost:8000/api/core/system/status/
```

### Logs
```bash
# Application logs
docker-compose logs web

# Celery logs
docker-compose logs celery_worker

# Database logs
docker-compose logs db
```

### Metrics
- AI usage analytics
- API performance metrics
- User activity tracking
- Error rate monitoring

## 🛠️ Development Tools

### VS Code Setup
Recommended extensions (see `.vscode/extensions.json`):
- Python
- Django
- Pylance
- REST Client
- Docker
- GitLens

### Code Quality
```bash
# Format code
black .
isort .

# Lint code
flake8

# Run tests
pytest
```

### Database Management
```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py loaddata fixtures/sample_data.json
```

## 🔒 Security

### Production Security
- Change all default passwords
- Use strong SECRET_KEY
- Enable HTTPS in production
- Configure proper CORS settings
- Set up proper firewall rules

### API Security
- Token-based authentication
- Rate limiting
- Request validation
- SQL injection protection
- XSS protection

### Data Protection
- Encrypted sensitive data
- Secure API key storage
- User data isolation
- GDPR compliance ready

## 📈 Performance

### Optimization
- Database query optimization
- Redis caching
- Static file compression
- CDN integration ready
- Lazy loading for AI features

### Scaling
- Horizontal scaling with load balancers
- Multiple Celery workers
- Database read replicas
- Redis clustering support

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

### Code Standards
- Follow PEP 8
- Write comprehensive tests
- Document API changes
- Update README as needed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help
- Check the documentation
- Review API examples
- Search existing issues
- Create detailed bug reports

### Common Issues
- **AI API errors**: Check your OpenAI API key and quota
- **Database connection**: Verify MySQL credentials
- **Celery not working**: Ensure Redis is running
- **Static files missing**: Run `collectstatic`

## 🚀 Deployment

### Production Deployment
```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Manual deployment
gunicorn ai_productivity_platform.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4
```

### Environment Variables
Essential environment variables for production:
- `DEBUG=False`
- `SECRET_KEY=your-production-secret`
- `OPENAI_API_KEY=your-api-key`
- `ALLOWED_HOSTS=your-domain.com`

## 📞 Contact

For questions, suggestions, or support:
- Email: support@aiplatform.local
- Documentation: http://localhost:8000/docs
- Issues: GitHub Issues

---

**Built with ❤️ using Django, OpenAI, and modern web technologies**