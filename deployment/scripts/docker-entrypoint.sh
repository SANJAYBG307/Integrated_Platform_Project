#!/bin/bash

# AI Productivity Platform Docker Entrypoint Script
# This script handles the startup sequence for the Django application

set -e

echo "Starting AI Productivity Platform..."

# Change to backend directory
cd /app/backend

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z db 3306; do
    echo "Database not ready, waiting..."
    sleep 2
done
echo "Database is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
    echo "Redis not ready, waiting..."
    sleep 2
done
echo "Redis is ready!"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create cache table
echo "Creating cache table..."
python manage.py createcachetable || true

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@aiplatform.local',
            password='admin123',
            full_name='Platform Administrator'
        )
        print("Superuser created successfully!")
    else:
        print("Superuser already exists.")
except IntegrityError:
    print("Superuser creation failed - user may already exist.")
EOF

# Load initial data
echo "Loading initial AI templates and configuration..."
python manage.py shell << EOF
from apps.ai_engine.models import AIProvider, AIModel, AITemplate

# Create OpenAI provider if it doesn't exist
provider, created = AIProvider.objects.get_or_create(
    name='openai',
    defaults={
        'display_name': 'OpenAI',
        'api_endpoint': 'https://api.openai.com/v1',
        'is_active': True,
        'max_tokens': 4000,
        'rate_limit_per_minute': 60
    }
)

if created:
    print("Created OpenAI provider")

# Create AI models
models_data = [
    {
        'model_name': 'gpt-3.5-turbo',
        'display_name': 'GPT-3.5 Turbo',
        'description': 'Fast and efficient model for most tasks',
        'max_tokens': 4096,
        'cost_per_1k_tokens': 0.002,
        'is_active': True,
        'capabilities': {
            'text_generation': True,
            'summarization': True,
            'analysis': True
        }
    },
    {
        'model_name': 'gpt-4',
        'display_name': 'GPT-4',
        'description': 'Most capable model for complex tasks',
        'max_tokens': 8192,
        'cost_per_1k_tokens': 0.03,
        'is_active': True,
        'capabilities': {
            'text_generation': True,
            'summarization': True,
            'analysis': True,
            'reasoning': True
        }
    }
]

for model_data in models_data:
    model, created = AIModel.objects.get_or_create(
        provider=provider,
        model_name=model_data['model_name'],
        defaults=model_data
    )
    if created:
        print(f"Created AI model: {model_data['display_name']}")

# Create AI templates
templates_data = [
    {
        'name': 'Note Summarizer',
        'template_type': 'summarize',
        'prompt_template': 'Please provide a concise summary of the following text in 2-3 sentences: {content}',
        'system_message': 'You are an expert at creating clear, concise summaries. Focus on the main points and key insights.',
        'max_tokens': 150,
        'temperature': 0.3,
        'is_active': True
    },
    {
        'name': 'Keyword Extractor',
        'template_type': 'extract_keywords',
        'prompt_template': 'Extract {count} most important keywords from this text. Return only a JSON array of keywords: {content}',
        'system_message': 'You are an expert at identifying key terms and concepts. Return only a valid JSON array.',
        'max_tokens': 100,
        'temperature': 0.1,
        'is_active': True
    },
    {
        'name': 'Sentiment Analyzer',
        'template_type': 'analyze_sentiment',
        'prompt_template': 'Analyze the sentiment of this text. Respond with only one word: positive, negative, or neutral: {content}',
        'system_message': 'You are an expert at sentiment analysis. Be concise and accurate.',
        'max_tokens': 10,
        'temperature': 0.1,
        'is_active': True
    },
    {
        'name': 'Task Breakdown',
        'template_type': 'task_breakdown',
        'prompt_template': 'Break down this task into 3-5 specific, actionable subtasks. Return as a JSON array: {content}',
        'system_message': 'You are an expert project manager. Create clear, specific subtasks that can be completed independently.',
        'max_tokens': 200,
        'temperature': 0.2,
        'is_active': True
    },
    {
        'name': 'Priority Analyzer',
        'template_type': 'priority_analysis',
        'prompt_template': 'Analyze the priority of this task considering urgency and importance. Context: {context}. Task: {content}. Respond with: low, medium, high, or urgent.',
        'system_message': 'You are an expert at task prioritization using principles like the Eisenhower Matrix.',
        'max_tokens': 20,
        'temperature': 0.1,
        'is_active': True
    },
    {
        'name': 'Time Estimator',
        'template_type': 'time_estimation',
        'prompt_template': 'Estimate how many minutes this task would take to complete: {content}. Respond with only the number.',
        'system_message': 'You are an expert at time estimation. Consider task complexity and typical completion times.',
        'max_tokens': 10,
        'temperature': 0.1,
        'is_active': True
    }
]

for template_data in templates_data:
    template, created = AITemplate.objects.get_or_create(
        name=template_data['name'],
        template_type=template_data['template_type'],
        defaults=template_data
    )
    if created:
        print(f"Created AI template: {template_data['name']}")

print("Initial data loading completed!")
EOF

# Start the application using supervisor
echo "Starting application services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf