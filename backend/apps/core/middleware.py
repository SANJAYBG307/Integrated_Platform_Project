"""
Custom middleware for the AI Productivity Platform.
"""

import time
import json
from django.http import JsonResponse
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import RateLimitRule, APIKeyUsage


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware with configurable rules.
    """

    def process_request(self, request):
        # Skip rate limiting for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None

        # Get applicable rate limit rules
        rules = RateLimitRule.objects.filter(is_active=True)

        for rule in rules:
            if self._matches_pattern(request.path, rule.endpoint_pattern):
                if not self._check_rate_limit(request, rule):
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f'Too many requests. Limit: {rule.max_requests} per {rule.time_window} seconds'
                    }, status=429)

        return None

    def _matches_pattern(self, path, pattern):
        """Check if path matches the pattern."""
        import re
        # Convert simple patterns to regex
        if '*' in pattern:
            pattern = pattern.replace('*', '.*')
        try:
            return bool(re.match(pattern, path))
        except re.error:
            return path.startswith(pattern)

    def _check_rate_limit(self, request, rule):
        """Check if request exceeds rate limit."""
        # Determine user type
        user_type = self._get_user_type(request.user)

        if rule.user_type != 'all' and rule.user_type != user_type:
            return True

        # Create cache key
        if isinstance(request.user, AnonymousUser):
            identifier = request.META.get('REMOTE_ADDR', 'unknown')
        else:
            identifier = f"user_{request.user.id}"

        cache_key = f"rate_limit_{rule.id}_{identifier}"

        # Get current count from cache
        current_count = cache.get(cache_key, 0)

        if current_count >= rule.max_requests:
            return False

        # Increment counter
        cache.set(cache_key, current_count + 1, rule.time_window)
        return True

    def _get_user_type(self, user):
        """Determine user type for rate limiting."""
        if isinstance(user, AnonymousUser):
            return 'anonymous'
        elif hasattr(user, 'is_premium') and user.is_premium:
            return 'premium'
        else:
            return 'free'


class APIUsageTrackingMiddleware(MiddlewareMixin):
    """
    Track API usage for analytics and monitoring.
    """

    def process_request(self, request):
        request._start_time = time.time()
        request._request_size = len(request.body) if request.body else 0
        return None

    def process_response(self, request, response):
        # Only track API endpoints
        if not request.path.startswith('/api/'):
            return response

        # Skip if user is not authenticated
        if isinstance(request.user, AnonymousUser):
            return response

        try:
            response_time = time.time() - getattr(request, '_start_time', time.time())
            request_size = getattr(request, '_request_size', 0)
            response_size = len(response.content) if hasattr(response, 'content') else 0

            # Create usage record
            APIKeyUsage.objects.create(
                user=request.user,
                endpoint=request.path,
                method=request.method,
                response_status=response.status_code,
                response_time=response_time,
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                request_size=request_size,
                response_size=response_size,
            )
        except Exception:
            # Don't let tracking errors break the request
            pass

        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to responses.
    """

    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Add CSP header for HTML responses
        if response.get('Content-Type', '').startswith('text/html'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdnjs.cloudflare.com; "
                "connect-src 'self' https://api.openai.com;"
            )

        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log requests for debugging and monitoring.
    """

    def process_request(self, request):
        # Log API requests
        if request.path.startswith('/api/'):
            import logging
            logger = logging.getLogger('api_requests')

            log_data = {
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if not isinstance(request.user, AnonymousUser) else 'anonymous',
                'ip': request.META.get('REMOTE_ADDR', ''),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }

            logger.info(f"API Request: {json.dumps(log_data)}")

        return None