from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    # API endpoints
    path('categories/', views.CategoryListCreateView.as_view(), name='api_category_list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='api_category_detail'),
    path('tags/', views.TagListCreateView.as_view(), name='api_tag_list'),
    path('', views.NoteListCreateView.as_view(), name='api_note_list'),
    path('<int:pk>/', views.NoteDetailView.as_view(), name='api_note_detail'),
    path('<int:note_id>/versions/', views.NoteVersionListView.as_view(), name='api_note_versions'),
    path('<int:note_id>/ai-analyze/', views.trigger_ai_analysis, name='api_trigger_ai'),
    path('search/', views.search_notes, name='api_search'),

    # Web views
    path('list/', views.note_list, name='list'),
    path('detail/<int:pk>/', views.note_detail, name='detail'),
    path('create/', views.note_create, name='create'),
    path('edit/<int:pk>/', views.note_edit, name='edit'),
]