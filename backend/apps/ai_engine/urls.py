from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    # AI Usage and Quota
    path('quota/', views.AIUsageQuotaView.as_view(), name='quota'),
    path('usage-logs/', views.AIRequestLogListView.as_view(), name='usage_logs'),
    path('analytics/', views.ai_usage_analytics, name='analytics'),

    # AI Insights
    path('insights/', views.AIInsightListView.as_view(), name='insights'),
    path('insights/<int:insight_id>/read/', views.mark_insight_read, name='mark_insight_read'),
    path('insights/generate/', views.generate_insights, name='generate_insights'),

    # AI Analysis Endpoints
    path('analyze/text/', views.analyze_text, name='analyze_text'),
    path('analyze/task/', views.analyze_task, name='analyze_task'),
]