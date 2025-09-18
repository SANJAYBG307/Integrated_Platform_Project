#!/bin/bash

# AI Productivity Platform - Startup Script
# This script helps you start the platform with the new organized structure

echo "🚀 AI Productivity Platform - Starting..."

# Check if we're in the right directory
if [ ! -f "PROJECT_STRUCTURE.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to start with Docker
start_docker() {
    echo "🐳 Starting with Docker..."

    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo "📝 Creating .env file from example..."
        cp .env.example .env
        echo "⚠️  Please edit .env file with your OpenAI API key and other settings"
        echo "   Required: OPENAI_API_KEY=your-api-key-here"
        return 1
    fi

    # Navigate to deployment directory
    cd deployment/docker

    # Start services
    echo "🚀 Starting Docker services..."
    docker-compose up -d

    # Check status
    echo "📊 Service status:"
    docker-compose ps

    # Show access URLs
    echo ""
    echo "✅ Platform started successfully!"
    echo "📱 Access URLs:"
    echo "   Main Application: http://localhost:8000"
    echo "   Admin Panel: http://localhost:8000/admin"
    echo "   API Docs: http://localhost:8000/api/docs"
    echo "   Celery Monitor: http://localhost:5555"
    echo ""
    echo "📋 Default credentials:"
    echo "   Admin: admin / admin123"
    echo "   Database: Saas_User / Saas@123"
    echo ""
    echo "📝 To view logs: docker-compose logs -f web"
    echo "🛑 To stop: docker-compose down"
}

# Function to start locally
start_local() {
    echo "💻 Starting local development..."

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "🐍 Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate

    # Install dependencies
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt

    # Navigate to backend
    cd backend

    # Run migrations
    echo "🗄️ Running database migrations..."
    python manage.py migrate

    # Create superuser if it doesn't exist
    echo "👤 Creating admin user..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created: admin / admin123')
else:
    print('Admin user already exists: admin / admin123')
"

    # Collect static files
    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput

    # Start development server
    echo "🚀 Starting development server..."
    echo "📱 Access URL: http://localhost:8000"
    echo "🛑 Press Ctrl+C to stop"
    python manage.py runserver
}

# Function to show help
show_help() {
    echo "🚀 AI Productivity Platform - Startup Script"
    echo ""
    echo "Usage: ./start.sh [option]"
    echo ""
    echo "Options:"
    echo "  docker    Start with Docker (recommended)"
    echo "  local     Start local development server"
    echo "  help      Show this help message"
    echo ""
    echo "📁 Project Structure:"
    echo "  backend/     - Django backend application"
    echo "  frontend/    - Templates and static files"
    echo "  database/    - Database scripts and fixtures"
    echo "  deployment/  - Docker and deployment configs"
    echo "  docs/        - Documentation"
    echo "  config/      - Development configurations"
    echo ""
    echo "📚 Documentation:"
    echo "  docs/user/setup.md - Detailed setup guide"
    echo "  docs/README.md     - Project overview"
    echo "  PROJECT_STRUCTURE.md - Folder organization"
}

# Main logic
case "${1:-docker}" in
    "docker")
        start_docker
        ;;
    "local")
        start_local
        ;;
    "help")
        show_help
        ;;
    *)
        echo "❌ Unknown option: $1"
        show_help
        exit 1
        ;;
esac