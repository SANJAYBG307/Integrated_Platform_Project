from rest_framework import serializers
from .models import TaskList, Task, Subtask, TaskComment, TaskReminder, ProductivityMetrics


class TaskListSerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = TaskList
        fields = ('id', 'name', 'description', 'color', 'icon', 'is_default', 'task_count', 'created_at')

    def get_task_count(self, obj):
        return obj.tasks.count()


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ('id', 'title', 'is_completed', 'order', 'created_at', 'completed_at')


class TaskCommentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = TaskComment
        fields = ('id', 'content', 'user_email', 'is_ai_generated', 'created_at')


class TaskListSerializer(serializers.ModelSerializer):
    subtasks = SubtaskSerializer(many=True, read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    task_list_name = serializers.CharField(source='task_list.name', read_only=True)
    days_until_due = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'task_list', 'task_list_name',
            'priority', 'status', 'due_date', 'estimated_duration',
            'is_pinned', 'order', 'tags', 'days_until_due', 'is_overdue',
            'subtasks', 'comments', 'created_at', 'updated_at', 'completed_at'
        )


class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubtaskSerializer(many=True, read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    task_list_name = serializers.CharField(source='task_list.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    days_until_due = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'task_list', 'task_list_name',
            'priority', 'status', 'due_date', 'estimated_duration',
            'ai_priority_suggestion', 'ai_time_estimate', 'ai_subtasks', 'ai_context',
            'is_pinned', 'order', 'tags', 'days_until_due', 'is_overdue',
            'subtasks', 'comments', 'user_email',
            'created_at', 'updated_at', 'completed_at', 'last_ai_processed'
        )


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'title', 'description', 'task_list', 'priority', 'status',
            'due_date', 'estimated_duration', 'is_pinned', 'tags'
        )

    def create(self, validated_data):
        task = Task.objects.create(user=self.context['request'].user, **validated_data)
        return task


class SubtaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ('title', 'order')

    def create(self, validated_data):
        task_id = self.context['task_id']
        return Subtask.objects.create(task_id=task_id, **validated_data)


class TaskCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComment
        fields = ('content',)

    def create(self, validated_data):
        task_id = self.context['task_id']
        user = self.context['request'].user
        return TaskComment.objects.create(
            task_id=task_id,
            user=user,
            **validated_data
        )


class TaskReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskReminder
        fields = ('id', 'reminder_time', 'reminder_type', 'message', 'is_sent', 'created_at')


class ProductivityMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductivityMetrics
        fields = (
            'date', 'tasks_created', 'tasks_completed', 'tasks_overdue',
            'total_estimated_time', 'avg_completion_time',
            'ai_suggestions_used', 'ai_processing_requests',
            'productivity_score', 'ai_insights'
        )