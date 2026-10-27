from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Like, Comment, Follow, Notification


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a Profile object whenever a new User registers.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()


@receiver(post_save, sender=Like)
def notify_on_like(sender, instance, created, **kwargs):
    """
    Notifies the post owner when a user likes their post.
    """
    if created and instance.user != instance.post.user:
        Notification.objects.create(
            recipient=instance.post.user,
            sender=instance.user,
            notification_type='like',
            post=instance.post
        )


@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    """
    Notifies the post owner when a user comments on their post.
    """
    if created and instance.user != instance.post.user:
        Notification.objects.create(
            recipient=instance.post.user,
            sender=instance.user,
            notification_type='comment',
            post=instance.post
        )


@receiver(post_save, sender=Follow)
def notify_on_follow(sender, instance, created, **kwargs):
    """
    Notifies the target user when a new follower follows them.
    """
    if created:
        Notification.objects.create(
            recipient=instance.following,
            sender=instance.follower,
            notification_type='follow'
        )
