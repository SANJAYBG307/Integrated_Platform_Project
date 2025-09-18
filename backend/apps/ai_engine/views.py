from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import AITemplate, AIUsageQuota, AIRequestLog, AIInsight
from .services import get_ai_service, AIServiceError, AIQuotaExceededError
from .tasks import generate_productivity_insights
import logging

logger = logging.getLogger(__name__)


class AIUsageQuotaView(generics.RetrieveAPIView):
    """
    Get current user's AI usage quota information.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        quotas = AIUsageQuota.objects.filter(
            user=request.user,
            is_active=True
        )

        quota_data = {}
        for quota in quotas:
            quota.reset_if_needed()  # Reset if needed
            quota_data[quota.quota_type] = {
                'max_requests': quota.max_requests,
                'used_requests': quota.used_requests,
                'requests_remaining': quota.requests_remaining,
                'max_tokens': quota.max_tokens,
                'used_tokens': quota.used_tokens,
                'tokens_remaining': quota.tokens_remaining,
                'reset_date': quota.reset_date,
            }

        return Response(quota_data)


class AIRequestLogListView(generics.ListAPIView):
    """
    List user's AI request history.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIRequestLog.objects.filter(user=self.request.user)[:50]

    def list(self, request):
        queryset = self.get_queryset()
        data = []

        for log in queryset:
            data.append({
                'id': log.id,
                'request_type': log.request_type,
                'success': log.success,
                'tokens_total': log.tokens_total,
                'response_time': log.response_time,
                'cost_usd': log.cost_usd,
                'created_at': log.created_at,
                'error_message': log.error_message if not log.success else None,
            })

        return Response(data)


class AIInsightListView(generics.ListAPIView):
    """
    List user's AI-generated insights.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIInsight.objects.filter(
            user=self.request.user,
            expires_at__isnull=True  # Only non-expired insights
        ).order_by('-created_at')

    def list(self, request):
        queryset = self.get_queryset()
        data = []

        for insight in queryset:
            data.append({
                'id': insight.id,
                'insight_type': insight.insight_type,
                'title': insight.title,
                'content': insight.content,
                'confidence_score': insight.confidence_score,
                'is_read': insight.is_read,
                'is_actionable': insight.is_actionable,
                'created_at': insight.created_at,
            })

        return Response(data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_insight_read(request, insight_id):
    """Mark an insight as read."""
    try:
        insight = AIInsight.objects.get(id=insight_id, user=request.user)
        insight.is_read = True
        insight.save(update_fields=['is_read'])
        return Response({'message': 'Insight marked as read'})
    except AIInsight.DoesNotExist:
        return Response({'error': 'Insight not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_text(request):
    """
    Analyze text with AI for various purposes.
    """
    text = request.data.get('text', '')
    analysis_type = request.data.get('type', 'summarize')

    if not text:
        return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)

    if len(text.split()) < 5:
        return Response({'error': 'Text too short for analysis'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        ai_service = get_ai_service(user=request.user)

        result = {}
        if analysis_type == 'summarize':
            length = request.data.get('length', 'medium')
            result['summary'] = ai_service.summarize_text(
                text,
                length=length,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

        elif analysis_type == 'keywords':
            count = request.data.get('count', 8)
            result['keywords'] = ai_service.extract_keywords(
                text,
                count=count,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

        elif analysis_type == 'sentiment':
            result['sentiment'] = ai_service.analyze_sentiment(
                text,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

        elif analysis_type == 'topics':
            result['topics'] = ai_service.identify_topics(
                text,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

        elif analysis_type == 'tags':
            existing_tags = request.data.get('existing_tags', [])
            result['suggested_tags'] = ai_service.suggest_tags(
                text,
                existing_tags=existing_tags,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

        elif analysis_type == 'all':
            # Run all analyses
            result['summary'] = ai_service.summarize_text(text)
            result['keywords'] = ai_service.extract_keywords(text)
            result['sentiment'] = ai_service.analyze_sentiment(text)
            result['topics'] = ai_service.identify_topics(text)

        else:
            return Response({'error': 'Invalid analysis type'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'analysis_type': analysis_type,
            'results': result
        })

    except AIQuotaExceededError as e:
        logger.warning(f"AI quota exceeded for user {request.user}: {e}")
        return Response({
            'error': 'AI quota exceeded',
            'message': str(e)
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    except AIServiceError as e:
        logger.error(f"AI service error for user {request.user}: {e}")
        return Response({
            'error': 'AI service error',
            'message': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    except Exception as e:
        logger.error(f"Unexpected error in analyze_text: {e}")
        return Response({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_task(request):
    """
    Analyze a task with AI for priority, time estimation, and subtask breakdown.
    """
    title = request.data.get('title', '')
    description = request.data.get('description', '')

    if not title:
        return Response({'error': 'Task title is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        ai_service = get_ai_service(user=request.user)
        full_text = f"{title}\n{description}" if description else title

        result = {}

        # Analyze priority
        context = request.data.get('context', '')
        result['suggested_priority'] = ai_service.analyze_task_priority(
            title,
            context=context,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Estimate time
        result['estimated_time'] = ai_service.estimate_task_time(
            full_text,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Break down into subtasks
        result['suggested_subtasks'] = ai_service.break_down_task(
            full_text,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        return Response({
            'success': True,
            'results': result
        })

    except AIQuotaExceededError as e:
        return Response({
            'error': 'AI quota exceeded',
            'message': str(e)
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    except AIServiceError as e:
        return Response({
            'error': 'AI service error',
            'message': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    except Exception as e:
        logger.error(f"Unexpected error in analyze_task: {e}")
        return Response({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_insights(request):
    """
    Trigger generation of productivity insights for the user.
    """
    try:
        task = generate_productivity_insights.delay(request.user.id)
        return Response({
            'message': 'Insights generation started',
            'task_id': task.id
        })
    except Exception as e:
        logger.error(f"Error triggering insights generation: {e}")
        return Response({
            'error': 'Failed to start insights generation',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_usage_analytics(request):
    """
    Get AI usage analytics for the user.
    """
    try:
        from datetime import datetime, timedelta
        from django.db.models import Count, Sum, Avg

        # Get usage for last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)

        logs = AIRequestLog.objects.filter(
            user=request.user,
            created_at__gte=thirty_days_ago
        )

        analytics = {
            'total_requests': logs.count(),
            'successful_requests': logs.filter(success=True).count(),
            'failed_requests': logs.filter(success=False).count(),
            'total_tokens_used': logs.aggregate(total=Sum('tokens_total'))['total'] or 0,
            'total_cost': logs.aggregate(total=Sum('cost_usd'))['total'] or 0.0,
            'avg_response_time': logs.aggregate(avg=Avg('response_time'))['avg'] or 0.0,
            'request_types': logs.values('request_type').annotate(count=Count('id')),
            'daily_usage': []
        }

        # Get daily breakdown
        for i in range(7):  # Last 7 days
            date = datetime.now().date() - timedelta(days=i)
            daily_logs = logs.filter(created_at__date=date)
            analytics['daily_usage'].append({
                'date': date.isoformat(),
                'requests': daily_logs.count(),
                'tokens': daily_logs.aggregate(total=Sum('tokens_total'))['total'] or 0,
                'cost': daily_logs.aggregate(total=Sum('cost_usd'))['total'] or 0.0,
            })

        return Response(analytics)

    except Exception as e:
        logger.error(f"Error generating AI analytics: {e}")
        return Response({
            'error': 'Failed to generate analytics',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)