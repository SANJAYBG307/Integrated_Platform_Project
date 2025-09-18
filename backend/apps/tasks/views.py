from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import TaskList, Task, Subtask, TaskComment, TaskReminder, ProductivityMetrics
from .serializers import (
    TaskListSerializer, TaskListSerializer as TaskSerializer, TaskDetailSerializer,
    TaskCreateUpdateSerializer, SubtaskSerializer, SubtaskCreateUpdateSerializer,
    TaskCommentSerializer, TaskCommentCreateSerializer, TaskReminderSerializer,
    ProductivityMetricsSerializer
)


# API Views
class TaskListListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskListDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskList.objects.filter(user=self.request.user)


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)

        # Filtering
        task_list = self.request.query_params.get('list')
        status_filter = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        overdue = self.request.query_params.get('overdue')
        search = self.request.query_params.get('search')

        if task_list:
            queryset = queryset.filter(task_list_id=task_list)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority:
            queryset = queryset.filter(priority=priority)
        if overdue == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now(),
                status__in=['todo', 'in_progress']
            )
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )

        # Ordering
        ordering = self.request.query_params.get('ordering', 'order')
        if ordering in ['title', '-title', 'created_at', '-created_at', 'due_date', '-due_date', 'priority', '-priority']:
            queryset = queryset.order_by(ordering)

        return queryset.select_related('task_list').prefetch_related('subtasks', 'comments')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateUpdateSerializer
        return TaskSerializer


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskCreateUpdateSerializer
        return TaskDetailSerializer


class SubtaskListCreateView(generics.ListCreateAPIView):
    serializer_class = SubtaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id, user=self.request.user)
        return Subtask.objects.filter(task=task)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubtaskCreateUpdateSerializer
        return SubtaskSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['task_id'] = self.kwargs['task_id']
        return context


class SubtaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubtaskCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id, user=self.request.user)
        return Subtask.objects.filter(task=task)


class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id, user=self.request.user)
        return TaskComment.objects.filter(task=task)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCommentCreateSerializer
        return TaskCommentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['task_id'] = self.kwargs['task_id']
        return context


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_task_completed(request, task_id):
    """Mark a task as completed."""
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.mark_completed()
        return Response({'message': 'Task marked as completed'})
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_subtask_completed(request, task_id, subtask_id):
    """Mark a subtask as completed."""
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        subtask = Subtask.objects.get(id=subtask_id, task=task)
        subtask.mark_completed()
        return Response({'message': 'Subtask marked as completed'})
    except (Task.DoesNotExist, Subtask.DoesNotExist):
        return Response({'error': 'Task or subtask not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def trigger_ai_task_analysis(request, task_id):
    """Manually trigger AI analysis for a task."""
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        from ai_engine.tasks import process_task_with_ai
        task_result = process_task_with_ai.delay(task.id)
        return Response({
            'message': 'AI analysis started',
            'task_id': task_result.id
        })
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def productivity_dashboard(request):
    """Get productivity metrics and insights."""
    user = request.user
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # Get recent metrics
    recent_metrics = ProductivityMetrics.objects.filter(
        user=user,
        date__gte=week_ago
    ).order_by('-date')

    # Calculate current stats
    tasks_today = Task.objects.filter(
        user=user,
        created_at__date=today
    ).count()

    completed_today = Task.objects.filter(
        user=user,
        completed_at__date=today
    ).count()

    overdue_tasks = Task.objects.filter(
        user=user,
        due_date__lt=timezone.now(),
        status__in=['todo', 'in_progress']
    ).count()

    serializer = ProductivityMetricsSerializer(recent_metrics, many=True)

    return Response({
        'recent_metrics': serializer.data,
        'today_stats': {
            'tasks_created': tasks_today,
            'tasks_completed': completed_today,
            'overdue_tasks': overdue_tasks,
        }
    })


# Web Views
@login_required
def task_dashboard(request):
    """Main task dashboard view."""
    user = request.user
    today = timezone.now().date()

    # Get user's task lists
    task_lists = TaskList.objects.filter(user=user)

    # Get tasks by status
    todo_tasks = Task.objects.filter(user=user, status='todo')[:5]
    in_progress_tasks = Task.objects.filter(user=user, status='in_progress')[:5]
    completed_today = Task.objects.filter(user=user, completed_at__date=today)

    # Get overdue tasks
    overdue_tasks = Task.objects.filter(
        user=user,
        due_date__lt=timezone.now(),
        status__in=['todo', 'in_progress']
    )

    context = {
        'task_lists': task_lists,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_today': completed_today,
        'overdue_tasks': overdue_tasks,
        'total_tasks': Task.objects.filter(user=user).count(),
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required
def task_list_view(request, list_id=None):
    """View tasks in a specific list."""
    user = request.user

    if list_id:
        task_list = get_object_or_404(TaskList, id=list_id, user=user)
        tasks = Task.objects.filter(user=user, task_list=task_list)
    else:
        task_list = None
        tasks = Task.objects.filter(user=user)

    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    search = request.GET.get('search')
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    context = {
        'task_list': task_list,
        'tasks': tasks,
        'task_lists': TaskList.objects.filter(user=user),
        'status_filter': status_filter,
        'search_query': search,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_detail_view(request, pk):
    """Detailed view of a single task."""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    context = {
        'task': task,
        'subtasks': task.subtasks.all(),
        'comments': task.comments.all(),
        'task_lists': TaskList.objects.filter(user=request.user),
    }
    return render(request, 'tasks/task_detail.html', context)