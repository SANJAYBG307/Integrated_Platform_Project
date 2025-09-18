from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Category, Tag, Note, NoteShare, NoteVersion, AIRequest
from .serializers import (
    CategorySerializer, TagSerializer, NoteListSerializer,
    NoteDetailSerializer, NoteCreateUpdateSerializer,
    NoteShareSerializer, NoteVersionSerializer, AIRequestSerializer
)


# API Views
class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.annotate(note_count=Count('notes'))


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class TagListCreateView(generics.ListCreateAPIView):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Tag.objects.annotate(note_count=Count('notes'))


class NoteListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user)

        # Filtering
        category = self.request.query_params.get('category')
        tags = self.request.query_params.get('tags')
        status_filter = self.request.query_params.get('status')
        search = self.request.query_params.get('search')

        if category:
            queryset = queryset.filter(category_id=category)
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__id__in=tag_list).distinct()
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(ai_summary__icontains=search)
            )

        # Ordering
        ordering = self.request.query_params.get('ordering', '-updated_at')
        if ordering in ['title', '-title', 'created_at', '-created_at', 'updated_at', '-updated_at']:
            queryset = queryset.order_by(ordering)

        return queryset.select_related('category').prefetch_related('tags')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NoteCreateUpdateSerializer
        return NoteListSerializer


class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoteDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NoteCreateUpdateSerializer
        return NoteDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class NoteVersionListView(generics.ListAPIView):
    serializer_class = NoteVersionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        note_id = self.kwargs['note_id']
        note = get_object_or_404(Note, id=note_id, user=self.request.user)
        return NoteVersion.objects.filter(note=note)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def trigger_ai_analysis(request, note_id):
    """Manually trigger AI analysis for a note."""
    try:
        note = Note.objects.get(id=note_id, user=request.user)
        from ai_engine.tasks import process_note_with_ai
        task = process_note_with_ai.delay(note.id)
        return Response({
            'message': 'AI analysis started',
            'task_id': task.id
        })
    except Note.DoesNotExist:
        return Response({'error': 'Note not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_notes(request):
    """Advanced search with AI-powered features."""
    query = request.GET.get('q', '')
    if not query:
        return Response({'results': []})

    notes = Note.objects.filter(
        user=request.user
    ).filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(ai_summary__icontains=query) |
        Q(ai_keywords__icontains=query)
    )

    serializer = NoteListSerializer(notes[:20], many=True)
    return Response({'results': serializer.data})


# Web Views
@login_required
def note_list(request):
    """Web-based note list view."""
    notes = Note.objects.filter(user=request.user).select_related('category').prefetch_related('tags')

    # Filtering
    category_id = request.GET.get('category')
    if category_id:
        notes = notes.filter(category_id=category_id)

    search = request.GET.get('search')
    if search:
        notes = notes.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )

    # Pagination
    paginator = Paginator(notes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'search_query': search,
        'selected_category': category_id,
    }
    return render(request, 'notes/note_list.html', context)


@login_required
def note_detail(request, pk):
    """Web-based note detail view."""
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.increment_view_count()

    # Get recent versions
    versions = NoteVersion.objects.filter(note=note)[:5]

    context = {
        'note': note,
        'versions': versions,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    return render(request, 'notes/note_detail.html', context)


@login_required
def note_create(request):
    """Web-based note creation."""
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title'),
            'content': request.POST.get('content'),
            'category': request.POST.get('category') or None,
            'tags': request.POST.getlist('tags'),
            'status': request.POST.get('status', 'draft'),
            'is_pinned': request.POST.get('is_pinned') == 'on',
        }

        serializer = NoteCreateUpdateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            note = serializer.save()
            messages.success(request, 'Note created successfully!')
            return redirect('notes:detail', pk=note.pk)
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    return render(request, 'notes/note_form.html', context)


@login_required
def note_edit(request, pk):
    """Web-based note editing."""
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == 'POST':
        data = {
            'title': request.POST.get('title'),
            'content': request.POST.get('content'),
            'category': request.POST.get('category') or None,
            'tags': request.POST.getlist('tags'),
            'status': request.POST.get('status', 'draft'),
            'is_pinned': request.POST.get('is_pinned') == 'on',
        }

        serializer = NoteCreateUpdateSerializer(note, data=data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Note updated successfully!')
            return redirect('notes:detail', pk=note.pk)
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'note': note,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
        'selected_tags': list(note.tags.values_list('id', flat=True)),
    }
    return render(request, 'notes/note_form.html', context)