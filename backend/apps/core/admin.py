from django.contrib import admin
from .models import (
    SystemConfiguration, RateLimitRule, APIKeyUsage,
    BackgroundTask, UserNotification, SystemHealth
)


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'is_active', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('key', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RateLimitRule)
class RateLimitRuleAdmin(admin.ModelAdmin):
    list_display = ('endpoint_pattern', 'max_requests', 'time_window', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'created_at')
    search_fields = ('endpoint_pattern',)


@admin.register(APIKeyUsage)
class APIKeyUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'endpoint', 'method', 'response_status', 'response_time', 'created_at')
    list_filter = ('method', 'response_status', 'created_at')
    search_fields = ('user__email', 'endpoint', 'ip_address')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(BackgroundTask)
class BackgroundTaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'task_type', 'user', 'status', 'progress', 'created_at', 'duration')
    list_filter = ('task_type', 'status', 'created_at')
    search_fields = ('task_id', 'description', 'user__email')
    readonly_fields = ('created_at', 'duration')

    def duration(self, obj):
        return f"{obj.duration:.2f}s" if obj.duration else "N/A"
    duration.short_description = 'Duration'


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'is_dismissed', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_dismissed', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at', 'read_at', 'is_expired')

    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True


@admin.register(SystemHealth)
class SystemHealthAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'status', 'response_time', 'error_count', 'checked_at')
    list_filter = ('service_type', 'status', 'checked_at')
    readonly_fields = ('checked_at',)
    date_hierarchy = 'checked_at'