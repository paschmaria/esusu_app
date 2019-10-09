from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .models import User, Profile, Group


@receiver(post_save, sender=User)
def create_profile_and_token(sender, instance, created, **kwargs):
  """Reciever function to create User Profile and API Token once user account is created"""
  if created:
    Profile.objects.create(user=instance)
    Token.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
  """Reciever function to save User Profile on update"""
  instance.profile.save()