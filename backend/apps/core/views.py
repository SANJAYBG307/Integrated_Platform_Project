from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import BackgroundTask, UserNotification, SystemHealth, APIKeyUsage
from .tasks import check_system_health


class BackgroundTaskListView(generics.ListAPIView):
    """
    List user's background tasks.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BackgroundTask.objects.filter(user=self.request.user)[:20]

    def list(self, request):
        queryset = self.get_queryset()
        data = []

        for task in queryset:
            data.append({
                'id': task.id,
                'task_id': task.task_id,
                'task_type': task.task_type,
                'status': task.status,
                'description': task.description,
                'progress': task.progress,
                'current_step': task.current_step,
                'total_steps': task.total_steps,
                'result': task.result,
                'error_message': task.error_message,
                'duration': task.duration,
                'created_at': task.created_at,
                'completed_at': task.completed_at,
            })

        return Response(data)


class NotificationListView(generics.ListAPIView):
    """
    List user's notifications.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserNotification.objects.filter(
            user=self.request.user,
            is_dismissed=False
        ).order_by('-created_at')

    def list(self, request):
        queryset = self.get_queryset()
        data = []

        for notification in queryset:
            if notification.is_expired:
                continue

            data.append({
                'id': notification.id,
                'notification_type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'action_url': notification.action_url,
                'action_label': notification.action_label,
                'is_read': notification.is_read,
                'created_at': notification.created_at,
            })

        return Response(data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    try:
        notification = UserNotification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.mark_read()
        return Response({'message': 'Notification marked as read'})
    except UserNotification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def dismiss_notification(request, notification_id):
    """Dismiss a notification."""
    try:
        notification = UserNotification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.dismiss()
        return Response({'message': 'Notification dismissed'})
    except UserNotification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read for the user."""
    count = UserNotification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())

    return Response({
        'message': f'{count} notifications marked as read'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_data(request):
    """
    Get dashboard data for the authenticated user.
    """
    user = request.user
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    # Recent activity stats
    recent_api_usage = APIKeyUsage.objects.filter(
        user=user,
        created_at__gte=week_ago
    ).count()

    # Task summary
    from tasks.models import Task
    task_stats = {
        'total': Task.objects.filter(user=user).count(),
        'completed': Task.objects.filter(user=user, status='completed').count(),
        'in_progress': Task.objects.filter(user=user, status='in_progress').count(),
        'overdue': Task.objects.filter(
            user=user,
            due_date__lt=now,
            status__in=['todo', 'in_progress']
        ).count(),
    }

    # Notes summary
    from notes.models import Note
    note_stats = {
        'total': Note.objects.filter(user=user).count(),
        'recent': Note.objects.filter(
            user=user,
            created_at__gte=week_ago
        ).count(),
    }

    # AI usage summary
    from ai_engine.models import AIRequestLog
    ai_stats = AIRequestLog.objects.filter(
        user=user,
        created_at__gte=week_ago
    ).aggregate(
        total_requests=Count('id'),
        successful_requests=Count('id', filter=models.Q(success=True)),
        avg_response_time=Avg('response_time')
    )

    # Unread notifications
    unread_notifications = UserNotification.objects.filter(
        user=user,
        is_read=False,
        is_dismissed=False
    ).count()

    return Response({
        'user_stats': {
            'tasks': task_stats,
            'notes': note_stats,
            'ai_usage': ai_stats,
            'api_usage_week': recent_api_usage,
            'unread_notifications': unread_notifications,
        },
        'last_updated': now
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def system_status(request):
    """
    Get system status for administrators.
    """
    # Get recent health checks
    recent_health = SystemHealth.objects.filter(
        checked_at__gte=timezone.now() - timedelta(hours=1)
    ).order_by('service_type', '-checked_at')

    health_status = {}
    for health in recent_health:
        if health.service_type not in health_status:
            health_status[health.service_type] = {
                'status': health.status,
                'response_time': health.response_time,
                'last_checked': health.checked_at,
                'error_message': health.error_message
            }

    # Get background task stats
    task_stats = BackgroundTask.objects.aggregate(
        pending=Count('id', filter=models.Q(status='pending')),
        running=Count('id', filter=models.Q(status='running')),
        completed_today=Count(
            'id',
            filter=models.Q(
                status='completed',
                completed_at__date=timezone.now().date()
            )
        ),
        failed_today=Count(
            'id',
            filter=models.Q(
                status='failed',
                completed_at__date=timezone.now().date()
            )
        )
    )

    # Get API usage stats for today
    api_stats = APIKeyUsage.objects.filter(
        created_at__date=timezone.now().date()
    ).aggregate(
        total_requests=Count('id'),
        avg_response_time=Avg('response_time'),
        error_rate=Count('id', filter=models.Q(response_status__gte=400)) * 100.0 / Count('id')
    )

    return Response({
        'system_health': health_status,
        'background_tasks': task_stats,
        'api_usage': api_stats,
        'last_updated': timezone.now()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def trigger_health_check(request):
    """
    Manually trigger a system health check.
    """
    task = check_system_health.delay()
    return Response({
        'message': 'Health check started',
        'task_id': task.id
    })


# Web views
@login_required
def dashboard(request):
    """Main dashboard view."""
    context = {
        'user': request.user,
    }
    return render(request, 'core/dashboard.html', context)