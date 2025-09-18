"""
Celery tasks for AI processing.

This module contains all background tasks for AI operations,
ensuring the main application remains responsive while AI
processing happens asynchronously.
"""

import time
import logging
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from .services import get_ai_service, AIServiceError, AIQuotaExceededError

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_note_with_ai(self, note_id):
    """
    Process a note with AI to generate summary, keywords, sentiment, and topics.
    """
    try:
        from notes.models import Note  # Import here to avoid circular imports

        note = Note.objects.get(id=note_id)
        ai_service = get_ai_service(user=note.user)

        logger.info(f"Starting AI processing for note {note_id}: {note.title}")

        # Check if content is substantial enough for AI processing
        if len(note.content.split()) < 10:
            logger.info(f"Note {note_id} too short for AI processing")
            return {
                'note_id': note_id,
                'status': 'skipped',
                'reason': 'Content too short'
            }

        results = {}

        # Generate summary
        try:
            summary_length = note.user.ai_summary_length
            summary = ai_service.summarize_text(
                note.content,
                length=summary_length,
                content_type='note',
                content_id=note.id
            )
            note.ai_summary = summary
            results['summary'] = summary
            logger.info(f"Generated summary for note {note_id}")
        except Exception as e:
            logger.error(f"Failed to generate summary for note {note_id}: {e}")
            results['summary_error'] = str(e)

        # Extract keywords
        try:
            keywords = ai_service.extract_keywords(
                note.content,
                count=8,
                content_type='note',
                content_id=note.id
            )
            note.ai_keywords = keywords
            results['keywords'] = keywords
            logger.info(f"Extracted keywords for note {note_id}: {keywords}")
        except Exception as e:
            logger.error(f"Failed to extract keywords for note {note_id}: {e}")
            results['keywords_error'] = str(e)

        # Analyze sentiment
        try:
            sentiment = ai_service.analyze_sentiment(
                note.content,
                content_type='note',
                content_id=note.id
            )
            note.ai_sentiment = sentiment
            results['sentiment'] = sentiment
            logger.info(f"Analyzed sentiment for note {note_id}: {sentiment}")
        except Exception as e:
            logger.error(f"Failed to analyze sentiment for note {note_id}: {e}")
            results['sentiment_error'] = str(e)

        # Identify topics
        try:
            topics = ai_service.identify_topics(
                note.content,
                content_type='note',
                content_id=note.id
            )
            note.ai_topics = topics
            results['topics'] = topics
            logger.info(f"Identified topics for note {note_id}: {topics}")
        except Exception as e:
            logger.error(f"Failed to identify topics for note {note_id}: {e}")
            results['topics_error'] = str(e)

        # Mark as processed and save
        note.mark_ai_processed()

        logger.info(f"Completed AI processing for note {note_id}")

        return {
            'note_id': note_id,
            'status': 'completed',
            'results': results,
            'processing_time': time.time()
        }

    except Note.DoesNotExist:
        logger.error(f"Note {note_id} not found")
        return {
            'note_id': note_id,
            'status': 'error',
            'error': 'Note not found'
        }

    except AIQuotaExceededError as e:
        logger.warning(f"AI quota exceeded for note {note_id}: {e}")
        return {
            'note_id': note_id,
            'status': 'quota_exceeded',
            'error': str(e)
        }

    except AIServiceError as e:
        logger.error(f"AI service error for note {note_id}: {e}")
        # Retry on service errors
        raise self.retry(exc=e)

    except Exception as e:
        logger.error(f"Unexpected error processing note {note_id}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_task_with_ai(self, task_id):
    """
    Process a task with AI to suggest priority, time estimate, and subtasks.
    """
    try:
        from tasks.models import Task  # Import here to avoid circular imports

        task = Task.objects.get(id=task_id)
        ai_service = get_ai_service(user=task.user)

        logger.info(f"Starting AI processing for task {task_id}: {task.title}")

        # Prepare task context
        context = f"Description: {task.description}\n"
        if task.due_date:
            context += f"Due date: {task.due_date.strftime('%Y-%m-%d')}\n"
        if task.estimated_duration:
            context += f"Estimated duration: {task.estimated_duration} minutes\n"

        results = {}

        # Analyze priority
        try:
            priority = ai_service.analyze_task_priority(
                task.title,
                context=context,
                content_type='task',
                content_id=task.id
            )
            task.ai_priority_suggestion = priority
            results['priority'] = priority
            logger.info(f"Suggested priority for task {task_id}: {priority}")
        except Exception as e:
            logger.error(f"Failed to analyze priority for task {task_id}: {e}")
            results['priority_error'] = str(e)

        # Estimate time
        try:
            time_estimate = ai_service.estimate_task_time(
                f"{task.title}\n{task.description}",
                content_type='task',
                content_id=task.id
            )
            task.ai_time_estimate = time_estimate
            results['time_estimate'] = time_estimate
            logger.info(f"Estimated time for task {task_id}: {time_estimate} minutes")
        except Exception as e:
            logger.error(f"Failed to estimate time for task {task_id}: {e}")
            results['time_error'] = str(e)

        # Break down into subtasks
        try:
            subtasks = ai_service.break_down_task(
                f"{task.title}\n{task.description}",
                content_type='task',
                content_id=task.id
            )
            task.ai_subtasks = subtasks
            results['subtasks'] = subtasks
            logger.info(f"Generated subtasks for task {task_id}: {len(subtasks)} items")
        except Exception as e:
            logger.error(f"Failed to generate subtasks for task {task_id}: {e}")
            results['subtasks_error'] = str(e)

        # Mark as processed and save
        task.mark_ai_processed()

        logger.info(f"Completed AI processing for task {task_id}")

        return {
            'task_id': task_id,
            'status': 'completed',
            'results': results,
            'processing_time': time.time()
        }

    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        if isinstance(e, (AIQuotaExceededError, AIServiceError)):
            return {
                'task_id': task_id,
                'status': 'error',
                'error': str(e)
            }
        raise self.retry(exc=e)


@shared_task
def generate_productivity_insights(user_id):
    """
    Generate AI-powered productivity insights for a user.
    """
    try:
        from tasks.models import Task, ProductivityMetrics
        from ai_engine.models import AIInsight

        user = User.objects.get(id=user_id)
        ai_service = get_ai_service(user=user)

        logger.info(f"Generating productivity insights for user {user_id}")

        # Gather user data from last 30 days
        from datetime import datetime, timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # Task completion data
        completed_tasks = Task.objects.filter(
            user=user,
            status='completed',
            completed_at__gte=thirty_days_ago
        ).count()

        overdue_tasks = Task.objects.filter(
            user=user,
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        ).count()

        # Get recent productivity metrics
        recent_metrics = ProductivityMetrics.objects.filter(
            user=user,
            date__gte=thirty_days_ago.date()
        ).order_by('-date')

        # Calculate trends
        if recent_metrics.count() >= 7:
            avg_score = sum(m.productivity_score for m in recent_metrics) / recent_metrics.count()
            trend_data = {
                'avg_productivity_score': avg_score,
                'completed_tasks': completed_tasks,
                'overdue_tasks': overdue_tasks,
                'total_metrics_days': recent_metrics.count()
            }

            # Generate AI insight
            prompt = f"""
            Analyze this productivity data and provide insights:
            - Average productivity score: {avg_score:.2f}
            - Tasks completed (30 days): {completed_tasks}
            - Overdue tasks: {overdue_tasks}
            - Data available for {recent_metrics.count()} days

            Provide actionable insights and recommendations in 2-3 sentences.
            """

            try:
                insight_text = ai_service.process_text(
                    prompt,
                    'productivity_insights',
                    content_type='user_analytics',
                    content_id=user.id
                )['response_text']

                # Create insight record
                AIInsight.objects.create(
                    user=user,
                    insight_type='productivity_trend',
                    title='Monthly Productivity Analysis',
                    content=insight_text,
                    data=trend_data,
                    confidence_score=0.8,
                    is_actionable=True
                )

                logger.info(f"Generated productivity insight for user {user_id}")
                return {
                    'user_id': user_id,
                    'status': 'completed',
                    'insight_generated': True
                }

            except Exception as e:
                logger.error(f"Failed to generate AI insight for user {user_id}: {e}")
                return {
                    'user_id': user_id,
                    'status': 'error',
                    'error': str(e)
                }

        return {
            'user_id': user_id,
            'status': 'skipped',
            'reason': 'Insufficient data for insights'
        }

    except Exception as e:
        logger.error(f"Error generating insights for user {user_id}: {e}")
        return {
            'user_id': user_id,
            'status': 'error',
            'error': str(e)
        }


@shared_task
def cleanup_old_ai_logs():
    """
    Clean up old AI request logs to manage database size.
    """
    try:
        from ai_engine.models import AIRequestLog
        from datetime import timedelta

        # Delete logs older than 90 days
        cutoff_date = timezone.now() - timedelta(days=90)
        deleted_count = AIRequestLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]

        logger.info(f"Cleaned up {deleted_count} old AI request logs")
        return {
            'status': 'completed',
            'deleted_count': deleted_count
        }

    except Exception as e:
        logger.error(f"Error cleaning up AI logs: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def generate_daily_ai_reports():
    """
    Generate daily reports on AI usage and performance.
    """
    try:
        from ai_engine.models import AIRequestLog
        from datetime import date, timedelta

        yesterday = date.today() - timedelta(days=1)

        # Get yesterday's AI usage statistics
        logs = AIRequestLog.objects.filter(created_at__date=yesterday)

        stats = {
            'total_requests': logs.count(),
            'successful_requests': logs.filter(success=True).count(),
            'total_tokens': sum(log.tokens_total for log in logs),
            'total_cost': sum(log.cost_usd for log in logs),
            'avg_response_time': logs.aggregate(
                avg_time=models.Avg('response_time')
            )['avg_time'] or 0,
            'unique_users': logs.values('user').distinct().count(),
        }

        logger.info(f"Daily AI report for {yesterday}: {stats}")
        return {
            'date': yesterday.isoformat(),
            'status': 'completed',
            'stats': stats
        }

    except Exception as e:
        logger.error(f"Error generating daily AI report: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def reset_monthly_quotas():
    """
    Reset monthly AI usage quotas for all users.
    """
    try:
        from ai_engine.models import AIUsageQuota

        quotas = AIUsageQuota.objects.filter(
            quota_type='monthly',
            is_active=True
        )

        reset_count = 0
        for quota in quotas:
            quota.reset_if_needed()
            reset_count += 1

        logger.info(f"Processed {reset_count} monthly quotas for reset")
        return {
            'status': 'completed',
            'processed_count': reset_count
        }

    except Exception as e:
        logger.error(f"Error resetting monthly quotas: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }