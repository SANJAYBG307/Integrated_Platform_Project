from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SystemConfiguration(models.Model):
    """
    System-wide configuration settings.
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_system_config'

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"


class RateLimitRule(models.Model):
    """
    Rate limiting rules for API endpoints.
    """
    endpoint_pattern = models.CharField(max_length=255, help_text='URL pattern to match')
    max_requests = models.IntegerField(default=60)
    time_window = models.IntegerField(default=3600, help_text='Time window in seconds')
    user_type = models.CharField(
        max_length=20,
        choices=[
            ('all', 'All Users'),
            ('free', 'Free Users'),
            ('premium', 'Premium Users'),
            ('anonymous', 'Anonymous Users'),
        ],
        default='all'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_rate_limit_rule'

    def __str__(self):
        return f"{self.endpoint_pattern} - {self.max_requests}/{self.time_window}s"


class APIKeyUsage(models.Model):
    """
    Track API key usage for monitoring and billing.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_usage')
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    response_status = models.IntegerField()
    response_time = models.FloatField(help_text='Response time in seconds')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    request_size = models.IntegerField(default=0, help_text='Request size in bytes')
    response_size = models.IntegerField(default=0, help_text='Response size in bytes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_api_usage'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['endpoint']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.endpoint} - {self.created_at}"


class BackgroundTask(models.Model):
    """
    Track background tasks and their status.
    """
    TASK_TYPES = [
        ('ai_processing', 'AI Processing'),
        ('data_export', 'Data Export'),
        ('report_generation', 'Report Generation'),
        ('email_sending', 'Email Sending'),
        ('cleanup', 'Cleanup'),
        ('sync', 'Data Synchronization'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='background_tasks')
    task_id = models.CharField(max_length=255, unique=True)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Task details
    description = models.TextField()
    progress = models.IntegerField(default=0, help_text='Progress percentage 0-100')
    total_steps = models.IntegerField(default=1)
    current_step = models.IntegerField(default=0)

    # Results and metadata
    result = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_background_task'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task_type} - {self.status}"

    @property
    def duration(self):
        """Calculate task duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (timezone.now() - self.started_at).total_seconds()
        return 0

    def mark_started(self):
        """Mark task as started."""
        self.status = 'running'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def mark_completed(self, result=None):
        """Mark task as completed."""
        self.status = 'completed'
        self.progress = 100
        self.completed_at = timezone.now()
        if result:
            self.result = result
        self.save(update_fields=['status', 'progress', 'completed_at', 'result'])

    def mark_failed(self, error_message):
        """Mark task as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])

    def update_progress(self, step, total_steps=None):
        """Update task progress."""
        self.current_step = step
        if total_steps:
            self.total_steps = total_steps
        self.progress = int((step / self.total_steps) * 100)
        self.save(update_fields=['current_step', 'total_steps', 'progress'])


class UserNotification(models.Model):
    """
    In-app notifications for users.
    """
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('ai_insight', 'AI Insight'),
        ('task_reminder', 'Task Reminder'),
        ('system', 'System Message'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Metadata
    action_url = models.URLField(blank=True, help_text='URL for notification action')
    action_label = models.CharField(max_length=50, blank=True, help_text='Label for action button')
    metadata = models.JSONField(default=dict)

    # Status
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'core_notification'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def mark_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def dismiss(self):
        """Dismiss notification."""
        self.is_dismissed = True
        self.save(update_fields=['is_dismissed'])


class SystemHealth(models.Model):
    """
    System health monitoring data.
    """
    SERVICE_TYPES = [
        ('database', 'Database'),
        ('redis', 'Redis'),
        ('celery', 'Celery'),
        ('ai_api', 'AI API'),
        ('email', 'Email Service'),
        ('storage', 'File Storage'),
    ]

    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('unhealthy', 'Unhealthy'),
        ('unknown', 'Unknown'),
    ]

    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response_time = models.FloatField(help_text='Response time in seconds')
    error_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_system_health'
        ordering = ['-checked_at']

    def __str__(self):
        return f"{self.service_type} - {self.status} - {self.checked_at}"