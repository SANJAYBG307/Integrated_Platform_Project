#!/bin/bash

# AI Productivity Platform - Verification Script
# This script verifies that the project is properly configured for both Docker and local development

echo "🔍 AI Productivity Platform - Verification Starting..."

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
        return 0
    else
        echo "❌ $1 - MISSING"
        return 1
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1/"
        return 0
    else
        echo "❌ $1/ - MISSING"
        return 1
    fi
}

# Initialize error counter
errors=0

echo "📁 Checking Project Structure..."

# Check root level files
check_file "PROJECT_STRUCTURE.md" || ((errors++))
check_file "requirements.txt" || ((errors++))
check_file "start.sh" || ((errors++))
check_file ".env.example" || ((errors++))
check_file ".gitignore" || ((errors++))
check_file "LICENSE" || ((errors++))

# Check main directories
echo ""
echo "📂 Checking Main Directories..."
check_dir "backend" || ((errors++))
check_dir "frontend" || ((errors++))
check_dir "database" || ((errors++))
check_dir "deployment" || ((errors++))
check_dir "docs" || ((errors++))
check_dir "config" || ((errors++))

# Check backend structure
echo ""
echo "🐍 Checking Backend Structure..."
check_dir "backend/ai_productivity_platform" || ((errors++))
check_dir "backend/apps" || ((errors++))
check_file "backend/manage.py" || ((errors++))

# Check Django apps
echo ""
echo "📱 Checking Django Apps..."
check_dir "backend/apps/core" || ((errors++))
check_dir "backend/apps/ai_engine" || ((errors++))
check_dir "backend/apps/notes" || ((errors++))
check_dir "backend/apps/tasks" || ((errors++))
check_dir "backend/apps/users" || ((errors++))

# Check frontend structure
echo ""
echo "🎨 Checking Frontend Structure..."
check_dir "frontend/templates" || ((errors++))
check_dir "frontend/static" || ((errors++))
check_file "frontend/templates/base/main.html" || ((errors++))
check_file "frontend/static/css/main.css" || ((errors++))
check_file "frontend/static/js/main.js" || ((errors++))

# Check database files
echo ""
echo "🗄️ Checking Database Files..."
check_dir "database/scripts" || ((errors++))
check_dir "database/fixtures" || ((errors++))
check_file "database/scripts/init.sql" || ((errors++))
check_file "database/fixtures/sample_data.json" || ((errors++))

# Check deployment files
echo ""
echo "🚀 Checking Deployment Files..."
check_dir "deployment/docker" || ((errors++))
check_dir "deployment/environments" || ((errors++))
check_dir "deployment/scripts" || ((errors++))
check_file "deployment/docker/docker-compose.yml" || ((errors++))
check_file "deployment/docker/Dockerfile" || ((errors++))
check_file "deployment/environments/development.env" || ((errors++))
check_file "deployment/environments/production.env" || ((errors++))
check_file "deployment/scripts/docker-entrypoint.sh" || ((errors++))

# Check Docker configuration files
echo ""
echo "🐳 Checking Docker Configuration..."
check_dir "deployment/docker/nginx" || ((errors++))
check_dir "deployment/docker/supervisor" || ((errors++))
check_file "deployment/docker/nginx/nginx.conf" || ((errors++))
check_file "deployment/docker/supervisor/supervisord.conf" || ((errors++))

# Check documentation
echo ""
echo "📚 Checking Documentation..."
check_file "docs/README.md" || ((errors++))
check_file "docs/user/setup.md" || ((errors++))

# Check configuration files
echo ""
echo "⚙️ Checking Configuration Files..."
check_file "config/vscode/settings.json" || ((errors++))

# Check critical Python files
echo ""
echo "🐍 Checking Critical Python Files..."
check_file "backend/ai_productivity_platform/settings.py" || ((errors++))
check_file "backend/ai_productivity_platform/urls.py" || ((errors++))
check_file "backend/apps/core/middleware.py" || ((errors++))

# Verify executable permissions
echo ""
echo "🔐 Checking Executable Permissions..."
if [ -x "start.sh" ]; then
    echo "✅ start.sh is executable"
else
    echo "❌ start.sh is not executable"
    ((errors++))
fi

if [ -x "deployment/scripts/docker-entrypoint.sh" ]; then
    echo "✅ docker-entrypoint.sh is executable"
else
    echo "❌ docker-entrypoint.sh is not executable"
    ((errors++))
fi

# Check Python syntax (if Python is available)
echo ""
echo "🔍 Checking Python Syntax..."
if command -v python3 &> /dev/null; then
    cd backend
    if python3 -m py_compile ai_productivity_platform/settings.py; then
        echo "✅ Django settings.py syntax is valid"
    else
        echo "❌ Django settings.py has syntax errors"
        ((errors++))
    fi

    if python3 -m py_compile manage.py; then
        echo "✅ manage.py syntax is valid"
    else
        echo "❌ manage.py has syntax errors"
        ((errors++))
    fi
    cd ..
else
    echo "⚠️ Python3 not found - skipping syntax check"
fi

# Final report
echo ""
echo "📊 Verification Complete!"
echo "========================================"

if [ $errors -eq 0 ]; then
    echo "🎉 SUCCESS: All files and directories are properly organized!"
    echo ""
    echo "🚀 Ready to start:"
    echo "   Docker: ./start.sh docker"
    echo "   Local:  ./start.sh local"
    echo ""
    echo "📚 Documentation:"
    echo "   Setup Guide: docs/user/setup.md"
    echo "   Project Overview: docs/README.md"
    echo "   Structure Guide: PROJECT_STRUCTURE.md"
    echo ""
    echo "⚠️ Before starting:"
    echo "   1. Set your OpenAI API key in .env file"
    echo "   2. For local development: Install MySQL and Redis"
    echo "   3. For Docker: Ensure Docker and Docker Compose are installed"
    exit 0
else
    echo "❌ ERRORS FOUND: $errors issues need to be fixed"
    echo ""
    echo "Please address the missing files/directories above before proceeding."
    exit 1
fi