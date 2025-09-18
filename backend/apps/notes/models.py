from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

User = get_user_model()


class Category(models.Model):
    """
    Categories for organizing notes.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    icon = models.CharField(max_length=50, default='folder')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notes_category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Tags for flexible note organization.
    """
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notes_tag'
        ordering = ['name']

    def __str__(self):
        return self.name


class Note(models.Model):
    """
    Main Note model with AI integration capabilities.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    tags = models.ManyToManyField(Tag, blank=True, related_name='notes')

    # AI-generated content
    ai_summary = models.TextField(blank=True, help_text='AI-generated summary')
    ai_keywords = models.JSONField(default=list, help_text='AI-extracted keywords')
    ai_sentiment = models.CharField(max_length=20, blank=True, help_text='AI-analyzed sentiment')
    ai_topics = models.JSONField(default=list, help_text='AI-identified topics')

    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_pinned = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_ai_processed = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notes_note'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['is_pinned']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('notes:detail', kwargs={'pk': self.pk})

    @property
    def word_count(self):
        return len(self.content.split())

    @property
    def reading_time(self):
        """Estimate reading time in minutes (250 words per minute)."""
        words = self.word_count
        return max(1, round(words / 250))

    def increment_view_count(self):
        """Increment view count atomically."""
        Note.objects.filter(pk=self.pk).update(view_count=models.F('view_count') + 1)

    def needs_ai_processing(self):
        """Check if note needs AI processing."""
        if not self.last_ai_processed:
            return True
        return self.updated_at > self.last_ai_processed

    def mark_ai_processed(self):
        """Mark note as processed by AI."""
        self.last_ai_processed = timezone.now()
        self.save(update_fields=['last_ai_processed'])


class NoteShare(models.Model):
    """
    Share notes with other users or publicly.
    """
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_notes')
    shared_with = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='received_notes', help_text='Leave blank for public sharing'
    )
    share_token = models.CharField(max_length=100, unique=True)
    is_public = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notes_share'
        unique_together = ['note', 'shared_with']

    def __str__(self):
        if self.shared_with:
            return f"{self.note.title} shared with {self.shared_with.email}"
        return f"{self.note.title} shared publicly"

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class NoteVersion(models.Model):
    """
    Version history for notes.
    """
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='versions')
    title = models.CharField(max_length=255)
    content = models.TextField()
    version_number = models.IntegerField()
    change_summary = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notes_version'
        ordering = ['-version_number']
        unique_together = ['note', 'version_number']

    def __str__(self):
        return f"{self.note.title} v{self.version_number}"


class AIRequest(models.Model):
    """
    Track AI requests for analytics and debugging.
    """
    REQUEST_TYPES = [
        ('summarize', 'Summarize'),
        ('extract_keywords', 'Extract Keywords'),
        ('analyze_sentiment', 'Analyze Sentiment'),
        ('suggest_tags', 'Suggest Tags'),
        ('identify_topics', 'Identify Topics'),
        ('smart_search', 'Smart Search'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_requests')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, null=True, blank=True, related_name='ai_requests')
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES)
    input_text = models.TextField()
    response = models.JSONField()
    tokens_used = models.IntegerField(default=0)
    processing_time = models.FloatField(help_text='Processing time in seconds')
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notes_ai_request'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request_type} - {self.user.email} - {self.created_at}"