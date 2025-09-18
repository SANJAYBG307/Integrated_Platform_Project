from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # API endpoints for task lists
    path('lists/', views.TaskListListCreateView.as_view(), name='api_tasklist_list'),
    path('lists/<int:pk>/', views.TaskListDetailView.as_view(), name='api_tasklist_detail'),

    # API endpoints for tasks
    path('', views.TaskListCreateView.as_view(), name='api_task_list'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='api_task_detail'),
    path('<int:task_id>/complete/', views.mark_task_completed, name='api_task_complete'),
    path('<int:task_id>/ai-analyze/', views.trigger_ai_task_analysis, name='api_trigger_ai'),

    # API endpoints for subtasks
    path('<int:task_id>/subtasks/', views.SubtaskListCreateView.as_view(), name='api_subtask_list'),
    path('<int:task_id>/subtasks/<int:pk>/', views.SubtaskDetailView.as_view(), name='api_subtask_detail'),
    path('<int:task_id>/subtasks/<int:subtask_id>/complete/', views.mark_subtask_completed, name='api_subtask_complete'),

    # API endpoints for comments
    path('<int:task_id>/comments/', views.TaskCommentListCreateView.as_view(), name='api_comment_list'),

    # Dashboard and analytics
    path('dashboard/', views.productivity_dashboard, name='api_dashboard'),

    # Web views
    path('dashboard-view/', views.task_dashboard, name='dashboard'),
    path('list/', views.task_list_view, name='list'),
    path('list/<int:list_id>/', views.task_list_view, name='list_detail'),
    path('detail/<int:pk>/', views.task_detail_view, name='detail'),
]