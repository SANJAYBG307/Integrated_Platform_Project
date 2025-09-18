"""
AI Services for integrating with external AI APIs.

This module provides a unified interface for different AI providers
and handles all AI-related operations with proper error handling,
rate limiting, and usage tracking.
"""

import time
import json
import logging
import openai
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone
from .models import AIProvider, AIModel, AITemplate, AIUsageQuota, AIRequestLog

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors."""
    pass


class AIRateLimitError(AIServiceError):
    """Raised when rate limits are exceeded."""
    pass


class AIQuotaExceededError(AIServiceError):
    """Raised when user quota is exceeded."""
    pass


class BaseAIService:
    """
    Base class for AI service implementations.
    """

    def __init__(self, user=None):
        self.user = user
        self.provider = None
        self.model = None

    def check_quota(self, estimated_tokens: int = 0) -> bool:
        """Check if user has available quota."""
        if not self.user:
            return True

        quota = AIUsageQuota.objects.filter(
            user=self.user,
            quota_type='monthly',
            is_active=True
        ).first()

        if quota:
            quota.reset_if_needed()
            return quota.can_make_request(estimated_tokens)

        return True

    def log_request(self, request_data: Dict[str, Any]) -> AIRequestLog:
        """Log AI request for analytics and debugging."""
        return AIRequestLog.objects.create(
            user=self.user,
            **request_data
        )

    def update_quota(self, tokens_used: int):
        """Update user's quota usage."""
        if not self.user:
            return

        quota = AIUsageQuota.objects.filter(
            user=self.user,
            quota_type='monthly',
            is_active=True
        ).first()

        if quota:
            quota.consume_usage(tokens_used)


class OpenAIService(BaseAIService):
    """
    OpenAI API integration service.
    """

    def __init__(self, user=None):
        super().__init__(user)
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.provider = AIProvider.objects.filter(name='openai').first()
        self.model = AIModel.objects.filter(
            provider=self.provider,
            model_name=settings.AI_MODEL,
            is_active=True
        ).first()

    def _make_request(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Make a request to OpenAI API with error handling and retries.
        """
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=kwargs.get('model', settings.AI_MODEL),
                messages=messages,
                max_tokens=kwargs.get('max_tokens', settings.AI_MAX_TOKENS),
                temperature=kwargs.get('temperature', settings.AI_TEMPERATURE),
                n=1,
                stop=None,
            )

            response_time = time.time() - start_time

            # Extract response data
            response_data = {
                'success': True,
                'response_text': response.choices[0].message.content,
                'tokens_input': response.usage.prompt_tokens,
                'tokens_output': response.usage.completion_tokens,
                'tokens_total': response.usage.total_tokens,
                'response_time': response_time,
                'model_used': self.model,
            }

            # Calculate cost
            if self.model:
                response_data['cost_usd'] = (response.usage.total_tokens / 1000) * self.model.cost_per_1k_tokens

            return response_data

        except openai.RateLimitError as e:
            logger.warning(f"OpenAI rate limit exceeded for user {self.user}: {e}")
            raise AIRateLimitError("API rate limit exceeded. Please try again later.")

        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise AIServiceError("AI service authentication failed.")

        except openai.BadRequestError as e:
            logger.error(f"OpenAI bad request: {e}")
            raise AIServiceError(f"Invalid request: {e}")

        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {e}")
            raise AIServiceError(f"AI service error: {str(e)}")

    def process_text(self, text: str, request_type: str, template_name: str = None, **kwargs) -> Dict[str, Any]:
        """
        Process text using OpenAI with specified template and request type.
        """
        # Check quota first
        estimated_tokens = len(text.split()) * 1.3  # Rough estimation
        if not self.check_quota(int(estimated_tokens)):
            raise AIQuotaExceededError("Monthly AI quota exceeded.")

        # Get template
        template = None
        if template_name:
            template = AITemplate.objects.filter(
                name=template_name,
                template_type=request_type,
                is_active=True
            ).first()
        else:
            template = AITemplate.objects.filter(
                template_type=request_type,
                is_active=True
            ).first()

        if not template:
            raise AIServiceError(f"No active template found for {request_type}")

        # Format prompt
        try:
            prompt = template.format_prompt(content=text, **kwargs)
        except KeyError as e:
            raise AIServiceError(f"Template formatting error: missing variable {e}")

        # Prepare messages
        messages = []
        if template.system_message:
            messages.append({"role": "system", "content": template.system_message})
        messages.append({"role": "user", "content": prompt})

        # Make API request
        response_data = self._make_request(
            messages,
            max_tokens=template.max_tokens,
            temperature=template.temperature
        )

        # Log request
        log_data = {
            'request_type': request_type,
            'template_used': template,
            'input_text': text,
            'prompt_sent': prompt,
            'system_message': template.system_message,
            'ip_address': kwargs.get('ip_address'),
            'user_agent': kwargs.get('user_agent'),
            'content_object_type': kwargs.get('content_type'),
            'content_object_id': kwargs.get('content_id'),
            **response_data
        }

        self.log_request(log_data)

        # Update quota
        if response_data.get('tokens_total'):
            self.update_quota(response_data['tokens_total'])

        return response_data

    def summarize_text(self, text: str, length: str = 'medium', **kwargs) -> str:
        """Summarize text content."""
        template_name = f"summarize_{length}"
        response = self.process_text(text, 'summarize', template_name, **kwargs)
        return response.get('response_text', '')

    def extract_keywords(self, text: str, count: int = 10, **kwargs) -> List[str]:
        """Extract keywords from text."""
        response = self.process_text(text, 'extract_keywords', count=count, **kwargs)
        response_text = response.get('response_text', '')

        try:
            # Try to parse as JSON first
            keywords = json.loads(response_text)
            if isinstance(keywords, list):
                return keywords[:count]
        except json.JSONDecodeError:
            # Fallback to simple text parsing
            keywords = [k.strip() for k in response_text.split(',')]
            return keywords[:count]

        return []

    def analyze_sentiment(self, text: str, **kwargs) -> str:
        """Analyze sentiment of text."""
        response = self.process_text(text, 'analyze_sentiment', **kwargs)
        return response.get('response_text', '').lower().strip()

    def suggest_tags(self, text: str, existing_tags: List[str] = None, **kwargs) -> List[str]:
        """Suggest tags for content."""
        existing_tags_str = ', '.join(existing_tags) if existing_tags else ''
        response = self.process_text(
            text, 'suggest_tags',
            existing_tags=existing_tags_str,
            **kwargs
        )
        response_text = response.get('response_text', '')

        try:
            tags = json.loads(response_text)
            if isinstance(tags, list):
                return tags[:5]
        except json.JSONDecodeError:
            tags = [t.strip() for t in response_text.split(',')]
            return tags[:5]

        return []

    def identify_topics(self, text: str, **kwargs) -> List[str]:
        """Identify main topics in text."""
        response = self.process_text(text, 'identify_topics', **kwargs)
        response_text = response.get('response_text', '')

        try:
            topics = json.loads(response_text)
            if isinstance(topics, list):
                return topics
        except json.JSONDecodeError:
            topics = [t.strip() for t in response_text.split(',')]
            return topics

        return []

    def break_down_task(self, task_description: str, **kwargs) -> List[str]:
        """Break down a task into subtasks."""
        response = self.process_text(task_description, 'task_breakdown', **kwargs)
        response_text = response.get('response_text', '')

        try:
            subtasks = json.loads(response_text)
            if isinstance(subtasks, list):
                return subtasks
        except json.JSONDecodeError:
            # Parse numbered or bulleted list
            lines = response_text.split('\n')
            subtasks = []
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering/bullets
                    import re
                    clean_line = re.sub(r'^[\d\-•\.\)\s]+', '', line).strip()
                    if clean_line:
                        subtasks.append(clean_line)
            return subtasks

        return []

    def analyze_task_priority(self, task_description: str, context: str = '', **kwargs) -> str:
        """Analyze and suggest task priority."""
        full_text = f"{task_description}\n\nContext: {context}" if context else task_description
        response = self.process_text(full_text, 'priority_analysis', **kwargs)
        priority = response.get('response_text', '').lower().strip()

        # Normalize priority levels
        if 'urgent' in priority or 'critical' in priority:
            return 'urgent'
        elif 'high' in priority:
            return 'high'
        elif 'low' in priority:
            return 'low'
        else:
            return 'medium'

    def estimate_task_time(self, task_description: str, **kwargs) -> int:
        """Estimate time required for a task in minutes."""
        response = self.process_text(task_description, 'time_estimation', **kwargs)
        response_text = response.get('response_text', '')

        # Extract number from response
        import re
        numbers = re.findall(r'\d+', response_text)
        if numbers:
            return int(numbers[0])

        return 30  # Default fallback


# Factory function to get appropriate AI service
def get_ai_service(provider: str = 'openai', user=None) -> BaseAIService:
    """
    Factory function to get AI service instance.
    """
    if provider.lower() == 'openai':
        return OpenAIService(user)
    else:
        raise AIServiceError(f"Unsupported AI provider: {provider}")


# Convenience functions for common operations
def summarize_content(text: str, user=None, **kwargs) -> str:
    """Quick function to summarize content."""
    service = get_ai_service(user=user)
    return service.summarize_text(text, **kwargs)


def extract_content_keywords(text: str, user=None, **kwargs) -> List[str]:
    """Quick function to extract keywords."""
    service = get_ai_service(user=user)
    return service.extract_keywords(text, **kwargs)


def analyze_content_sentiment(text: str, user=None, **kwargs) -> str:
    """Quick function to analyze sentiment."""
    service = get_ai_service(user=user)
    return service.analyze_sentiment(text, **kwargs)