from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Note, NoteVersion
import uuid


@receiver(pre_save, sender=Note)
def create_note_version(sender, instance, **kwargs):
    """
    Create a version history entry when a note is updated.
    """
    if instance.pk:  # Only for existing notes
        try:
            old_note = Note.objects.get(pk=instance.pk)
            if old_note.content != instance.content or old_note.title != instance.title:
                # Create new version
                last_version = NoteVersion.objects.filter(note=instance).first()
                version_number = (last_version.version_number + 1) if last_version else 1

                NoteVersion.objects.create(
                    note=instance,
                    title=old_note.title,
                    content=old_note.content,
                    version_number=version_number,
                    change_summary=f"Updated {instance.updated_at.strftime('%Y-%m-%d %H:%M')}"
                )
        except Note.DoesNotExist:
            pass


@receiver(post_save, sender=Note)
def trigger_ai_processing(sender, instance, created, **kwargs):
    """
    Trigger AI processing for new or updated notes.
    """
    if instance.needs_ai_processing():
        # Import here to avoid circular imports
        from ai_engine.tasks import process_note_with_ai
        process_note_with_ai.delay(instance.id)