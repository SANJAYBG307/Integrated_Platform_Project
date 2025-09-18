from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import AIUsageQuota
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@receiver(post_save, sender=User)
def create_default_ai_quota(sender, instance, created, **kwargs):
    """
    Create default AI usage quota for new users.
    """
    if created:
        # Create monthly quota for free users
        quota_limits = {
            'monthly': {
                'max_requests': 100 if not instance.is_premium else 1000,
                'max_tokens': 10000 if not instance.is_premium else 100000,
                'reset_days': 30
            },
            'daily': {
                'max_requests': 10 if not instance.is_premium else 100,
                'max_tokens': 1000 if not instance.is_premium else 10000,
                'reset_days': 1
            }
        }

        for quota_type, limits in quota_limits.items():
            reset_date = timezone.now() + timedelta(days=limits['reset_days'])

            AIUsageQuota.objects.create(
                user=instance,
                quota_type=quota_type,
                max_requests=limits['max_requests'],
                max_tokens=limits['max_tokens'],
                reset_date=reset_date,
                is_active=True
            )