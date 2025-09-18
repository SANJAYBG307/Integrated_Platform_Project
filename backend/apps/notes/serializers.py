from rest_framework import serializers
from .models import Category, Tag, Note, NoteShare, NoteVersion, AIRequest


class CategorySerializer(serializers.ModelSerializer):
    note_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'color', 'icon', 'note_count', 'created_at')

    def get_note_count(self, obj):
        return obj.notes.count()


class TagSerializer(serializers.ModelSerializer):
    note_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'note_count', 'created_at')

    def get_note_count(self, obj):
        return obj.notes.count()


class NoteListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    tag_names = serializers.StringRelatedField(source='tags', many=True, read_only=True)
    word_count = serializers.ReadOnlyField()
    reading_time = serializers.ReadOnlyField()

    class Meta:
        model = Note
        fields = (
            'id', 'title', 'category', 'category_name', 'tags', 'tag_names',
            'status', 'is_pinned', 'is_favorite', 'view_count', 'word_count',
            'reading_time', 'created_at', 'updated_at'
        )


class NoteDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    tag_names = serializers.StringRelatedField(source='tags', many=True, read_only=True)
    word_count = serializers.ReadOnlyField()
    reading_time = serializers.ReadOnlyField()
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Note
        fields = (
            'id', 'title', 'content', 'category', 'category_name', 'tags', 'tag_names',
            'ai_summary', 'ai_keywords', 'ai_sentiment', 'ai_topics',
            'status', 'is_pinned', 'is_favorite', 'view_count',
            'word_count', 'reading_time', 'user_email',
            'created_at', 'updated_at', 'last_ai_processed'
        )


class NoteCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)

    class Meta:
        model = Note
        fields = ('title', 'content', 'category', 'tags', 'status', 'is_pinned', 'is_favorite')

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        note = Note.objects.create(user=self.context['request'].user, **validated_data)
        note.tags.set(tags)
        return note


class NoteShareSerializer(serializers.ModelSerializer):
    note_title = serializers.CharField(source='note.title', read_only=True)
    shared_by_email = serializers.CharField(source='shared_by.email', read_only=True)
    shared_with_email = serializers.CharField(source='shared_with.email', read_only=True)

    class Meta:
        model = NoteShare
        fields = (
            'id', 'note', 'note_title', 'shared_by', 'shared_by_email',
            'shared_with', 'shared_with_email', 'share_token',
            'is_public', 'can_edit', 'expires_at', 'created_at'
        )
        read_only_fields = ('shared_by', 'share_token', 'created_at')


class NoteVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteVersion
        fields = ('id', 'version_number', 'title', 'content', 'change_summary', 'created_at')


class AIRequestSerializer(serializers.ModelSerializer):
    note_title = serializers.CharField(source='note.title', read_only=True)

    class Meta:
        model = AIRequest
        fields = (
            'id', 'note', 'note_title', 'request_type', 'tokens_used',
            'processing_time', 'success', 'created_at'
        )