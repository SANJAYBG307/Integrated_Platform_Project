"""
Core background tasks for system maintenance and monitoring.
"""

import logging
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.management import call_command
from datetime import timedelta
from .models import BackgroundTask, SystemHealth, UserNotification, APIKeyUsage

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def cleanup_expired_tasks():
    """
    Clean up expired background tasks and old data.
    """
    try:
        # Delete completed tasks older than 7 days
        cutoff_date = timezone.now() - timedelta(days=7)
        deleted_tasks = BackgroundTask.objects.filter(
            status__in=['completed', 'failed'],
            completed_at__lt=cutoff_date
        ).delete()[0]

        # Delete old API usage records (older than 90 days)
        api_cutoff = timezone.now() - timedelta(days=90)
        deleted_api_usage = APIKeyUsage.objects.filter(
            created_at__lt=api_cutoff
        ).delete()[0]

        # Delete expired notifications
        expired_notifications = UserNotification.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]

        logger.info(f"Cleanup completed: {deleted_tasks} tasks, {deleted_api_usage} API records, {expired_notifications} notifications")

        return {
            'status': 'completed',
            'deleted_tasks': deleted_tasks,
            'deleted_api_usage': deleted_api_usage,
            'deleted_notifications': expired_notifications
        }

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def check_system_health():
    """
    Check the health of various system components.
    """
    health_results = {}

    # Check database
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            start_time = timezone.now()
            cursor.execute("SELECT 1")
            response_time = (timezone.now() - start_time).total_seconds()

        SystemHealth.objects.create(
            service_type='database',
            status='healthy',
            response_time=response_time
        )
        health_results['database'] = 'healthy'

    except Exception as e:
        SystemHealth.objects.create(
            service_type='database',
            status='unhealthy',
            response_time=0,
            error_message=str(e)
        )
        health_results['database'] = 'unhealthy'
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    try:
        from django.core.cache import cache
        start_time = timezone.now()
        cache.set('health_check', 'test', 10)
        cache.get('health_check')
        response_time = (timezone.now() - start_time).total_seconds()

        SystemHealth.objects.create(
            service_type='redis',
            status='healthy',
            response_time=response_time
        )
        health_results['redis'] = 'healthy'

    except Exception as e:
        SystemHealth.objects.create(
            service_type='redis',
            status='unhealthy',
            response_time=0,
            error_message=str(e)
        )
        health_results['redis'] = 'unhealthy'
        logger.error(f"Redis health check failed: {e}")

    # Check Celery
    try:
        from celery import current_app
        start_time = timezone.now()
        # Try to get worker stats
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        response_time = (timezone.now() - start_time).total_seconds()

        if stats:
            SystemHealth.objects.create(
                service_type='celery',
                status='healthy',
                response_time=response_time,
                metadata={'active_workers': len(stats)}
            )
            health_results['celery'] = 'healthy'
        else:
            SystemHealth.objects.create(
                service_type='celery',
                status='degraded',
                response_time=response_time,
                error_message='No active workers found'
            )
            health_results['celery'] = 'degraded'

    except Exception as e:
        SystemHealth.objects.create(
            service_type='celery',
            status='unhealthy',
            response_time=0,
            error_message=str(e)
        )
        health_results['celery'] = 'unhealthy'
        logger.error(f"Celery health check failed: {e}")

    # Check AI API
    try:
        from ai_engine.services import get_ai_service
        ai_service = get_ai_service()

        start_time = timezone.now()
        # Simple test request
        response = ai_service.process_text(
            "Test",
            'summarize',
            content_type='health_check'
        )
        response_time = (timezone.now() - start_time).total_seconds()

        if response.get('success'):
            SystemHealth.objects.create(
                service_type='ai_api',
                status='healthy',
                response_time=response_time
            )
            health_results['ai_api'] = 'healthy'
        else:
            SystemHealth.objects.create(
                service_type='ai_api',
                status='degraded',
                response_time=response_time,
                error_message='AI API returned error'
            )
            health_results['ai_api'] = 'degraded'

    except Exception as e:
        SystemHealth.objects.create(
            service_type='ai_api',
            status='unhealthy',
            response_time=0,
            error_message=str(e)
        )
        health_results['ai_api'] = 'unhealthy'
        logger.error(f"AI API health check failed: {e}")

    logger.info(f"System health check completed: {health_results}")
    return health_results


@shared_task
def send_notification_to_user(user_id, notification_type, title, message, **kwargs):
    """
    Send an in-app notification to a user.
    """
    try:
        user = User.objects.get(id=user_id)

        notification = UserNotification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=kwargs.get('action_url', ''),
            action_label=kwargs.get('action_label', ''),
            metadata=kwargs.get('metadata', {}),
            expires_at=kwargs.get('expires_at')
        )

        logger.info(f"Notification sent to user {user_id}: {title}")
        return {
            'status': 'completed',
            'notification_id': notification.id
        }

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for notification")
        return {
            'status': 'error',
            'error': 'User not found'
        }

    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def generate_usage_reports():
    """
    Generate daily usage reports and analytics.
    """
    try:
        from datetime import date
        from django.db.models import Count, Avg, Sum

        yesterday = date.today() - timedelta(days=1)

        # API usage stats
        api_stats = APIKeyUsage.objects.filter(
            created_at__date=yesterday
        ).aggregate(
            total_requests=Count('id'),
            avg_response_time=Avg('response_time'),
            total_data_transferred=Sum('request_size') + Sum('response_size')
        )

        # User activity stats
        active_users = User.objects.filter(
            last_login__date=yesterday
        ).count()

        # AI usage stats
        from ai_engine.models import AIRequestLog
        ai_stats = AIRequestLog.objects.filter(
            created_at__date=yesterday
        ).aggregate(
            total_ai_requests=Count('id'),
            successful_ai_requests=Count('id', filter=models.Q(success=True)),
            total_tokens=Sum('tokens_total'),
            total_ai_cost=Sum('cost_usd')
        )

        report_data = {
            'date': yesterday.isoformat(),
            'api_usage': api_stats,
            'active_users': active_users,
            'ai_usage': ai_stats
        }

        logger.info(f"Usage report generated for {yesterday}: {report_data}")
        return {
            'status': 'completed',
            'report_data': report_data
        }

    except Exception as e:
        logger.error(f"Error generating usage report: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def backup_database():
    """
    Create a database backup.
    """
    try:
        import os
        from django.conf import settings

        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.json')

        # Create Django fixture backup
        with open(backup_file, 'w') as f:
            call_command('dumpdata', stdout=f, format='json', indent=2)

        file_size = os.path.getsize(backup_file)

        logger.info(f"Database backup created: {backup_file} ({file_size} bytes)")
        return {
            'status': 'completed',
            'backup_file': backup_file,
            'file_size': file_size
        }

    except Exception as e:
        logger.error(f"Error creating database backup: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def monitor_disk_space():
    """
    Monitor disk space and send alerts if low.
    """
    try:
        import shutil
        from django.conf import settings

        # Check disk space for media directory
        media_path = settings.MEDIA_ROOT
        total, used, free = shutil.disk_usage(media_path)

        # Convert to GB
        total_gb = total // (1024**3)
        used_gb = used // (1024**3)
        free_gb = free // (1024**3)

        usage_percent = (used / total) * 100

        # Alert if usage is over 90%
        if usage_percent > 90:
            # Send alert to superusers
            superusers = User.objects.filter(is_superuser=True)
            for admin in superusers:
                send_notification_to_user.delay(
                    admin.id,
                    'warning',
                    'Low Disk Space Alert',
                    f'Disk usage is at {usage_percent:.1f}%. Free space: {free_gb}GB'
                )

        logger.info(f"Disk space check: {usage_percent:.1f}% used, {free_gb}GB free")
        return {
            'status': 'completed',
            'usage_percent': usage_percent,
            'free_gb': free_gb,
            'total_gb': total_gb
        }

    except Exception as e:
        logger.error(f"Error monitoring disk space: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }