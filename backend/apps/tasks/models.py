from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

User = get_user_model()


class TaskList(models.Model):
    """
    Task lists for organizing tasks.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_lists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#28a745')  # Hex color
    icon = models.CharField(max_length=50, default='list')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tasks_tasklist'
        unique_together = ['user', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.user.email} - {self.name}"

    def save(self, *args, **kwargs):
        # Ensure only one default list per user
        if self.is_default:
            TaskList.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Task(models.Model):
    """
    Main Task model with AI-powered features.
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Task properties
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_duration = models.IntegerField(null=True, blank=True, help_text='Estimated duration in minutes')

    # AI-generated suggestions
    ai_priority_suggestion = models.CharField(max_length=20, blank=True, help_text='AI-suggested priority')
    ai_time_estimate = models.IntegerField(null=True, blank=True, help_text='AI-estimated duration in minutes')
    ai_subtasks = models.JSONField(default=list, help_text='AI-suggested subtasks')
    ai_context = models.TextField(blank=True, help_text='AI-generated context or tips')

    # Metadata
    is_pinned = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    tags = models.CharField(max_length=255, blank=True, help_text='Comma-separated tags')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_ai_processed = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tasks_task'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.pk})

    @property
    def is_overdue(self):
        if not self.due_date or self.status == 'completed':
            return False
        return timezone.now() > self.due_date

    @property
    def days_until_due(self):
        if not self.due_date:
            return None
        delta = self.due_date - timezone.now()
        return delta.days

    def mark_completed(self):
        """Mark task as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def needs_ai_processing(self):
        """Check if task needs AI processing."""
        if not self.last_ai_processed:
            return True
        return self.updated_at > self.last_ai_processed

    def mark_ai_processed(self):
        """Mark task as processed by AI."""
        self.last_ai_processed = timezone.now()
        self.save(update_fields=['last_ai_processed'])


class Subtask(models.Model):
    """
    Subtasks for breaking down main tasks.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tasks_subtask'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.task.title} - {self.title}"

    def mark_completed(self):
        """Mark subtask as completed."""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save(update_fields=['is_completed', 'completed_at'])


class TaskComment(models.Model):
    """
    Comments and notes on tasks.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tasks_comment'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment on {self.task.title}"


class TaskReminder(models.Model):
    """
    Reminders for tasks.
    """
    REMINDER_TYPES = [
        ('email', 'Email'),
        ('notification', 'In-App Notification'),
        ('both', 'Email and Notification'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.DateTimeField()
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, default='notification')
    message = models.TextField(blank=True)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tasks_reminder'
        ordering = ['reminder_time']

    def __str__(self):
        return f"Reminder for {self.task.title}"


class TaskActivity(models.Model):
    """
    Activity log for tasks.
    """
    ACTIVITY_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('status_changed', 'Status Changed'),
        ('completed', 'Completed'),
        ('commented', 'Commented'),
        ('ai_processed', 'AI Processed'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tasks_activity'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.activity_type} - {self.task.title}"


class ProductivityMetrics(models.Model):
    """
    Daily productivity metrics for users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productivity_metrics')
    date = models.DateField()

    # Task metrics
    tasks_created = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    tasks_overdue = models.IntegerField(default=0)

    # Time metrics
    total_estimated_time = models.IntegerField(default=0)  # in minutes
    avg_completion_time = models.FloatField(default=0.0)  # in hours

    # AI metrics
    ai_suggestions_used = models.IntegerField(default=0)
    ai_processing_requests = models.IntegerField(default=0)

    # Productivity score (calculated by AI)
    productivity_score = models.FloatField(default=0.0)
    ai_insights = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tasks_productivity_metrics'
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.date}"