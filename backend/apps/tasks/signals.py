from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Task, TaskActivity, TaskList


@receiver(post_save, sender=Task)
def create_task_activity(sender, instance, created, **kwargs):
    """
    Create activity log when task is created or updated.
    """
    if created:
        TaskActivity.objects.create(
            task=instance,
            user=instance.user,
            activity_type='created',
            description=f'Task "{instance.title}" was created',
            metadata={'priority': instance.priority, 'status': instance.status}
        )
    else:
        # Check if status changed
        if hasattr(instance, '_original_status') and instance._original_status != instance.status:
            TaskActivity.objects.create(
                task=instance,
                user=instance.user,
                activity_type='status_changed',
                description=f'Task status changed from {instance._original_status} to {instance.status}',
                metadata={'old_status': instance._original_status, 'new_status': instance.status}
            )


@receiver(pre_save, sender=Task)
def track_status_changes(sender, instance, **kwargs):
    """
    Track original status for change detection.
    """
    if instance.pk:
        try:
            original = Task.objects.get(pk=instance.pk)
            instance._original_status = original.status

            # Auto-set completed_at when marking as completed
            if instance.status == 'completed' and original.status != 'completed':
                instance.completed_at = timezone.now()
            elif instance.status != 'completed' and original.status == 'completed':
                instance.completed_at = None

        except Task.DoesNotExist:
            pass


@receiver(post_save, sender=Task)
def trigger_ai_task_processing(sender, instance, created, **kwargs):
    """
    Trigger AI processing for new or updated tasks.
    """
    if instance.needs_ai_processing():
        # Import here to avoid circular imports
        from ai_engine.tasks import process_task_with_ai
        process_task_with_ai.delay(instance.id)


@receiver(post_save, sender=TaskList)
def ensure_default_task_list(sender, instance, created, **kwargs):
    """
    Ensure user has at least one task list.
    """
    if created:
        # Check if user has any other task lists
        user_lists = TaskList.objects.filter(user=instance.user)
        if user_lists.count() == 1:  # This is the first list
            instance.is_default = True
            instance.save(update_fields=['is_default'])