from django.contrib import admin
from .models import TaskList, Task, Subtask, TaskComment, TaskReminder, TaskActivity, ProductivityMetrics


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_default', 'created_at')
    list_filter = ('is_default', 'created_at')
    search_fields = ('name', 'user__email')


class SubtaskInline(admin.TabularInline):
    model = Subtask
    extra = 0


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'task_list', 'priority', 'status', 'due_date', 'is_overdue', 'created_at')
    list_filter = ('priority', 'status', 'task_list', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'last_ai_processed')
    inlines = [SubtaskInline, TaskCommentInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'task_list', 'title', 'description')
        }),
        ('Task Properties', {
            'fields': ('priority', 'status', 'due_date', 'estimated_duration', 'tags')
        }),
        ('AI Suggestions', {
            'fields': ('ai_priority_suggestion', 'ai_time_estimate', 'ai_subtasks', 'ai_context', 'last_ai_processed'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_pinned', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'


@admin.register(Subtask)
class SubtaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'is_completed', 'order', 'created_at')
    list_filter = ('is_completed', 'created_at')
    search_fields = ('title', 'task__title')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'is_ai_generated', 'created_at')
    list_filter = ('is_ai_generated', 'created_at')
    search_fields = ('content', 'task__title', 'user__email')


@admin.register(TaskReminder)
class TaskReminderAdmin(admin.ModelAdmin):
    list_display = ('task', 'reminder_time', 'reminder_type', 'is_sent', 'created_at')
    list_filter = ('reminder_type', 'is_sent', 'created_at')
    search_fields = ('task__title', 'message')


@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'activity_type', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('task__title', 'user__email', 'description')


@admin.register(ProductivityMetrics)
class ProductivityMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'tasks_completed', 'productivity_score', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at',)