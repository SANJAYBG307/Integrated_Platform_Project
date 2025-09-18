from django.contrib import admin
from .models import AIProvider, AIModel, AITemplate, AIUsageQuota, AIRequestLog, AIInsight


@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'is_active', 'rate_limit_per_minute', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'display_name')


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'provider', 'model_name', 'max_tokens', 'cost_per_1k_tokens', 'is_active')
    list_filter = ('provider', 'is_active')
    search_fields = ('model_name', 'display_name')


@admin.register(AITemplate)
class AITemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'is_active', 'created_at')
    list_filter = ('template_type', 'is_active', 'created_at')
    search_fields = ('name', 'template_type')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Prompt Configuration', {
            'fields': ('prompt_template', 'system_message')
        }),
        ('AI Parameters', {
            'fields': ('max_tokens', 'temperature')
        }),
    )


@admin.register(AIUsageQuota)
class AIUsageQuotaAdmin(admin.ModelAdmin):
    list_display = ('user', 'quota_type', 'used_requests', 'max_requests', 'used_tokens', 'max_tokens', 'reset_date')
    list_filter = ('quota_type', 'is_active', 'reset_date')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('requests_remaining', 'tokens_remaining')

    def requests_remaining(self, obj):
        return obj.requests_remaining
    requests_remaining.short_description = 'Requests Remaining'

    def tokens_remaining(self, obj):
        return obj.tokens_remaining
    tokens_remaining.short_description = 'Tokens Remaining'


@admin.register(AIRequestLog)
class AIRequestLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_type', 'model_used', 'success', 'tokens_total', 'cost_usd', 'response_time', 'created_at')
    list_filter = ('request_type', 'success', 'model_used', 'created_at')
    search_fields = ('user__email', 'request_type', 'error_message')
    readonly_fields = ('created_at', 'total_cost')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'request_type', 'model_used', 'template_used')
        }),
        ('Content', {
            'fields': ('input_text', 'prompt_sent', 'system_message', 'response_text'),
            'classes': ('collapse',)
        }),
        ('Performance', {
            'fields': ('tokens_input', 'tokens_output', 'tokens_total', 'response_time', 'cost_usd', 'total_cost')
        }),
        ('Status', {
            'fields': ('success', 'error_message', 'error_code')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'content_object_type', 'content_object_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def total_cost(self, obj):
        return f"${obj.total_cost:.4f}"
    total_cost.short_description = 'Calculated Cost'


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ('user', 'insight_type', 'title', 'confidence_score', 'is_read', 'is_actionable', 'created_at')
    list_filter = ('insight_type', 'is_read', 'is_actionable', 'created_at')
    search_fields = ('user__email', 'title', 'content')
    readonly_fields = ('created_at', 'updated_at', 'is_expired')

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'insight_type', 'title', 'confidence_score')
        }),
        ('Content', {
            'fields': ('content', 'data')
        }),
        ('Status', {
            'fields': ('is_read', 'is_actionable', 'action_taken', 'expires_at', 'is_expired')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True