from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import UserProfile

# Create a signal receiver to delete associated media files when a profile is deleted
@receiver(pre_delete, sender=UserProfile)
def delete_profile_media_files(sender, instance, **kwargs):
    # Delete the profile picture if it exists
    if instance.picture:
        instance.picture.delete()