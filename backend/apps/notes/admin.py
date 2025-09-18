from django.contrib import admin
from .models import Category, Tag, Note, NoteShare, NoteVersion, AIRequest


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


class NoteVersionInline(admin.TabularInline):
    model = NoteVersion
    extra = 0
    readonly_fields = ('version_number', 'created_at')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'is_pinned', 'view_count', 'created_at', 'updated_at')
    list_filter = ('status', 'is_pinned', 'is_favorite', 'category', 'created_at')
    search_fields = ('title', 'content', 'user__email')
    filter_horizontal = ('tags',)
    readonly_fields = ('view_count', 'last_ai_processed', 'created_at', 'updated_at')
    inlines = [NoteVersionInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'content', 'category', 'tags')
        }),
        ('AI Analysis', {
            'fields': ('ai_summary', 'ai_keywords', 'ai_sentiment', 'ai_topics', 'last_ai_processed'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('status', 'is_pinned', 'is_favorite', 'view_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NoteShare)
class NoteShareAdmin(admin.ModelAdmin):
    list_display = ('note', 'shared_by', 'shared_with', 'is_public', 'can_edit', 'expires_at', 'created_at')
    list_filter = ('is_public', 'can_edit', 'created_at', 'expires_at')
    search_fields = ('note__title', 'shared_by__email', 'shared_with__email')
    readonly_fields = ('share_token', 'created_at')


@admin.register(NoteVersion)
class NoteVersionAdmin(admin.ModelAdmin):
    list_display = ('note', 'version_number', 'change_summary', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('note__title', 'change_summary')
    readonly_fields = ('created_at',)


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_type', 'note', 'tokens_used', 'processing_time', 'success', 'created_at')
    list_filter = ('request_type', 'success', 'created_at')
    search_fields = ('user__email', 'note__title', 'request_type')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'note', 'request_type', 'input_text')
        }),
        ('Response', {
            'fields': ('response', 'success', 'error_message')
        }),
        ('Performance', {
            'fields': ('tokens_used', 'processing_time', 'created_at')
        }),
    )