from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Background tasks
    path('tasks/', views.BackgroundTaskListView.as_view(), name='background_tasks'),

    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<int:notification_id>/dismiss/', views.dismiss_notification, name='dismiss_notification'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    # Dashboard
    path('dashboard/', views.user_dashboard_data, name='dashboard_data'),

    # System admin endpoints
    path('system/status/', views.system_status, name='system_status'),
    path('system/health-check/', views.trigger_health_check, name='trigger_health_check'),

    # Web views
    path('dashboard-view/', views.dashboard, name='dashboard_view'),
]