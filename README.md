# 🧠 AI Productivity Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-v4.2+-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

A comprehensive, production-ready AI-integrated productivity platform built with Django, featuring intelligent note-taking, smart task management, and AI-powered insights.

## 🌟 Features

### 🤖 AI-Powered Intelligence
- **Smart Summarization** - Automatic note summarization with configurable length
- **Keyword Extraction** - AI-powered keyword identification
- **Sentiment Analysis** - Emotional tone analysis of content
- **Task Breakdown** - Intelligent task decomposition into subtasks
- **Priority Analysis** - AI-suggested task prioritization
- **Time Estimation** - Automated time estimation for tasks

### 📝 Productivity Tools
- **Rich Text Notes** - Create, edit, and organize notes with categories and tags
- **Smart Tasks** - Advanced task management with AI suggestions
- **Real-time Analytics** - AI-driven insights and productivity metrics
- **User Management** - Multi-user support with quotas and permissions

### 🔒 Enterprise Features
- **Rate Limiting** - Prevent API abuse with configurable limits
- **Usage Quotas** - Manage AI costs with user quotas
- **Security** - Enterprise-grade security with proper authentication
- **Monitoring** - Comprehensive logging and health checks
- **Scalability** - Built for high-performance production deployment

## 🏗️ Architecture

### Project Structure
```
ai-productivity-platform/
├── 📁 backend/                   # Django backend application
│   ├── 📁 ai_productivity_platform/  # Main Django project
│   └── 📁 apps/                  # Django applications (users, notes, tasks, ai_engine, core)
├── 📁 frontend/                  # Frontend assets and templates
│   ├── 📁 templates/             # HTML templates
│   └── 📁 static/                # CSS, JS, images
├── 📁 database/                  # Database related files
│   ├── 📁 scripts/               # Database scripts
│   └── 📁 fixtures/              # Sample data
├── 📁 deployment/                # Deployment configurations
│   ├── 📁 docker/                # Docker configurations
│   ├── 📁 environments/          # Environment files
│   └── 📁 scripts/               # Deployment scripts
├── 📁 docs/                      # Documentation
└── 📁 config/                    # Development configurations
```

### Technology Stack
- **Backend**: Django 4.2, Django REST Framework
- **Database**: MySQL 8.0
- **Cache/Queue**: Redis, Celery
- **AI**: OpenAI GPT-3.5/GPT-4
- **Frontend**: Bootstrap 5, JavaScript ES6+
- **Deployment**: Docker, Nginx, Supervisor

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### 1. Clone the Repository
```bash
git clone https://github.com/SANJAYBG307/Integrated_Platform_Project.git
cd Integrated_Platform_Project
```

### 2. Configure Environment
```bash
# Copy environment file
cp .env.example .env

# Edit .env file with your OpenAI API key
# Required: OPENAI_API_KEY=your-api-key-here
```

### 3. Start with Docker (Recommended)
```bash
# Start all services
./start.sh docker

# Access the application
# Main App: http://localhost:8000
# Admin Panel: http://localhost:8000/admin (admin/admin123)
# API Docs: http://localhost:8000/api/docs
# Celery Monitor: http://localhost:5555
```

### 4. Verification
```bash
# Verify everything is working
./verify.sh
```

## 📚 Documentation

- **[Testing Guide](TESTING_GUIDE.md)** - Complete testing procedures
- **[Operation Manual](OPERATION_MANUAL.md)** - Daily operations and maintenance
- **[Setup Guide](docs/user/setup.md)** - Detailed installation instructions
- **[Project Structure](PROJECT_STRUCTURE.md)** - Folder organization guide
- **[Verification Report](VERIFICATION_REPORT.md)** - Project verification results

## 💻 Development

### Local Development Setup
```bash
# Start local development
./start.sh local

# This will:
# - Create virtual environment
# - Install dependencies
# - Run migrations
# - Start development server
```

### Running Tests
```bash
# Navigate to backend directory
cd backend

# Run Django tests
python manage.py test

# Run specific app tests
python manage.py test apps.notes
```

## 🔧 Configuration

### Environment Variables
Key configuration options in `.env`:
```env
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Database
DB_NAME=Integrated_Platform
DB_USER=Saas_User
DB_PASSWORD=Saas@123

# AI Configuration
AI_MODEL=gpt-3.5-turbo
AI_MAX_TOKENS=150
AI_TEMPERATURE=0.7
```

## 📊 Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:8000/health/

# System status (admin required)
curl -H "Authorization: Token admin-token" \
  http://localhost:8000/api/core/system/status/
```

### Logs
```bash
# View application logs
docker-compose logs -f web

# View Celery logs
docker-compose logs -f celery_worker
```

## 🔒 Security Features

- Token-based authentication
- Rate limiting and request throttling
- SQL injection protection
- XSS protection
- CORS configuration
- Security headers
- Input validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Write comprehensive tests
- Update documentation for new features
- Ensure all tests pass before submitting PR

## 📄 API Documentation

### Authentication
```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Example API Calls
```bash
# List notes
curl -H "Authorization: Token your-token" \
  http://localhost:8000/api/notes/

# Create note with AI analysis
curl -X POST http://localhost:8000/api/notes/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"title": "Meeting Notes", "content": "Discussed project timeline and deliverables..."}'

# Get AI summary
curl -X POST http://localhost:8000/api/notes/1/summarize/ \
  -H "Authorization: Token your-token"
```

## 🆘 Support

### Getting Help
- Check the [Testing Guide](TESTING_GUIDE.md) for setup issues
- Review [Operation Manual](OPERATION_MANUAL.md) for usage questions
- Search existing issues before creating new ones
- Provide detailed error messages and logs when reporting issues

### Common Issues
- **AI API errors**: Check your OpenAI API key and quota
- **Database connection**: Verify MySQL credentials and service status
- **Celery not working**: Ensure Redis is running
- **Static files missing**: Run `python manage.py collectstatic`

## 📋 Requirements

### System Requirements
- **Python**: 3.11+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Memory**: 4GB+ recommended
- **Storage**: 10GB+ available space

### Python Dependencies
See [requirements.txt](requirements.txt) for complete list including:
- Django 4.2.7
- djangorestframework 3.14.0
- celery 5.3.4
- openai 1.3.8
- mysqlclient 2.2.0
- redis 5.0.1

## 🎯 Roadmap

- [ ] **Mobile App**: React Native mobile application
- [ ] **Advanced AI**: Custom model training and fine-tuning
- [ ] **Integrations**: Slack, Microsoft Teams, Google Workspace
- [ ] **Analytics**: Advanced productivity analytics dashboard
- [ ] **Multi-language**: Internationalization support
- [ ] **SSO**: Single Sign-On integration
- [ ] **Webhooks**: External system integrations

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- Built with [Django](https://www.djangoproject.com/) - The web framework for perfectionists
- Powered by [OpenAI](https://openai.com/) - AI integration
- UI components from [Bootstrap](https://getbootstrap.com/) - Responsive design framework
- Task processing by [Celery](https://docs.celeryproject.org/) - Distributed task queue

---

## 📞 Contact

**Project Maintainer**: SANJAYBG307
**Repository**: https://github.com/SANJAYBG307/Integrated_Platform_Project
**Issues**: https://github.com/SANJAYBG307/Integrated_Platform_Project/issues

---

**⭐ Star this repository if you find it helpful!**

Built with ❤️ using Django, OpenAI, and modern web technologies.