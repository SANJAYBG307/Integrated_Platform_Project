from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AIProvider(models.Model):
    """
    Configuration for different AI providers (OpenAI, Gemini, etc.).
    """
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    api_endpoint = models.URLField()
    is_active = models.BooleanField(default=True)
    max_tokens = models.IntegerField(default=4000)
    cost_per_token = models.FloatField(default=0.0, help_text='Cost per token in USD')
    rate_limit_per_minute = models.IntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_engine_provider'

    def __str__(self):
        return self.display_name


class AIModel(models.Model):
    """
    Available AI models for different providers.
    """
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='models')
    model_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    max_tokens = models.IntegerField()
    cost_per_1k_tokens = models.FloatField(help_text='Cost per 1000 tokens in USD')
    is_active = models.BooleanField(default=True)
    capabilities = models.JSONField(default=dict, help_text='Model capabilities and features')

    class Meta:
        db_table = 'ai_engine_model'
        unique_together = ['provider', 'model_name']

    def __str__(self):
        return f"{self.provider.name} - {self.display_name}"


class AITemplate(models.Model):
    """
    Predefined prompts and templates for different AI operations.
    """
    TEMPLATE_TYPES = [
        ('summarize', 'Summarize'),
        ('extract_keywords', 'Extract Keywords'),
        ('analyze_sentiment', 'Analyze Sentiment'),
        ('suggest_tags', 'Suggest Tags'),
        ('identify_topics', 'Identify Topics'),
        ('task_breakdown', 'Task Breakdown'),
        ('priority_analysis', 'Priority Analysis'),
        ('time_estimation', 'Time Estimation'),
        ('productivity_insights', 'Productivity Insights'),
    ]

    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    prompt_template = models.TextField(help_text='Template with placeholders like {content}')
    system_message = models.TextField(blank=True, help_text='System message for the AI model')
    max_tokens = models.IntegerField(default=150)
    temperature = models.FloatField(default=0.7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_engine_template'

    def __str__(self):
        return f"{self.name} ({self.template_type})"

    def format_prompt(self, **kwargs):
        """Format the prompt template with provided variables."""
        return self.prompt_template.format(**kwargs)


class AIUsageQuota(models.Model):
    """
    Track and manage AI usage quotas for users.
    """
    QUOTA_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_quotas')
    quota_type = models.CharField(max_length=20, choices=QUOTA_TYPES)
    max_requests = models.IntegerField()
    max_tokens = models.IntegerField()
    used_requests = models.IntegerField(default=0)
    used_tokens = models.IntegerField(default=0)
    reset_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_engine_usage_quota'
        unique_together = ['user', 'quota_type']

    def __str__(self):
        return f"{self.user.email} - {self.quota_type} quota"

    @property
    def requests_remaining(self):
        return max(0, self.max_requests - self.used_requests)

    @property
    def tokens_remaining(self):
        return max(0, self.max_tokens - self.used_tokens)

    def can_make_request(self, estimated_tokens=0):
        """Check if user can make another AI request."""
        if not self.is_active:
            return False
        if self.used_requests >= self.max_requests:
            return False
        if self.used_tokens + estimated_tokens > self.max_tokens:
            return False
        return True

    def consume_usage(self, tokens_used):
        """Update usage counters."""
        self.used_requests += 1
        self.used_tokens += tokens_used
        self.save(update_fields=['used_requests', 'used_tokens'])

    def reset_if_needed(self):
        """Reset quota if reset_date has passed."""
        if timezone.now() >= self.reset_date:
            self.used_requests = 0
            self.used_tokens = 0
            # Set next reset date
            if self.quota_type == 'daily':
                self.reset_date = timezone.now() + timezone.timedelta(days=1)
            elif self.quota_type == 'weekly':
                self.reset_date = timezone.now() + timezone.timedelta(weeks=1)
            elif self.quota_type == 'monthly':
                self.reset_date = timezone.now() + timezone.timedelta(days=30)
            self.save()


class AIRequestLog(models.Model):
    """
    Comprehensive logging of all AI requests for analytics and debugging.
    """
    REQUEST_TYPES = [
        ('summarize', 'Summarize'),
        ('extract_keywords', 'Extract Keywords'),
        ('analyze_sentiment', 'Analyze Sentiment'),
        ('suggest_tags', 'Suggest Tags'),
        ('identify_topics', 'Identify Topics'),
        ('task_breakdown', 'Task Breakdown'),
        ('priority_analysis', 'Priority Analysis'),
        ('time_estimation', 'Time Estimation'),
        ('smart_search', 'Smart Search'),
        ('productivity_insights', 'Productivity Insights'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_request_logs')
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES)
    model_used = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True)
    template_used = models.ForeignKey(AITemplate, on_delete=models.SET_NULL, null=True)

    # Request details
    input_text = models.TextField()
    prompt_sent = models.TextField()
    system_message = models.TextField(blank=True)

    # Response details
    response_text = models.TextField()
    response_json = models.JSONField(default=dict)

    # Performance metrics
    tokens_input = models.IntegerField(default=0)
    tokens_output = models.IntegerField(default=0)
    tokens_total = models.IntegerField(default=0)
    response_time = models.FloatField(help_text='Response time in seconds')
    cost_usd = models.FloatField(default=0.0)

    # Status and error handling
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    content_object_type = models.CharField(max_length=50, blank=True)  # 'note', 'task', etc.
    content_object_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_engine_request_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'request_type']),
            models.Index(fields=['success']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.request_type} - {self.created_at}"

    @property
    def total_cost(self):
        """Calculate total cost for this request."""
        if self.model_used:
            return (self.tokens_total / 1000) * self.model_used.cost_per_1k_tokens
        return 0.0


class AIInsight(models.Model):
    """
    Store AI-generated insights and analytics for users.
    """
    INSIGHT_TYPES = [
        ('productivity_trend', 'Productivity Trend'),
        ('task_pattern', 'Task Pattern'),
        ('time_management', 'Time Management'),
        ('content_analysis', 'Content Analysis'),
        ('goal_suggestion', 'Goal Suggestion'),
        ('habit_analysis', 'Habit Analysis'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_insights')
    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    data = models.JSONField(default=dict, help_text='Structured data for charts/graphs')
    confidence_score = models.FloatField(default=0.0, help_text='AI confidence score 0-1')

    # Metadata
    is_read = models.BooleanField(default=False)
    is_actionable = models.BooleanField(default=False)
    action_taken = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_engine_insight'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at