from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.templatetags.static import static
from django.db.models import Q, F


class ActivePostManager(models.Manager):
    """Manager to return only non-deleted posts."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Profile(models.Model):
    """
    User Profile model extending Django's auth.User (One-to-One).
    Stores profile metadata including bio, avatar, location, and website.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, default='')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def avatar_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return static('images/default-avatar.png')

    @property
    def display_name(self):
        full = self.user.get_full_name()
        return full if full.strip() else self.user.username

    @property
    def unread_notifications_count(self):
        return self.user.notifications.filter(is_read=False).count()


class Post(models.Model):
    """
    Post model storing user posts with optional media attachment and soft-deletion.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    # Custom & default managers
    objects = ActivePostManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_deleted', '-created_at']),
        ]

    def __str__(self):
        snippet = (self.content[:35] + '...') if len(self.content) > 35 else self.content
        return f"Post #{self.id} by @{self.user.username}: {snippet}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.filter(is_deleted=False).count()

    @property
    def active_comments(self):
        return self.comments.filter(is_deleted=False).select_related('user', 'user__profile')

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()


class Comment(models.Model):
    """
    Comment model allowing users to discuss posts.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]

    def __str__(self):
        return f"Comment #{self.id} by @{self.user.username} on Post #{self.post_id}"


class Like(models.Model):
    """
    Like model representing a user's like on a post.
    Constrained so a user can like a post only once.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='unique_post_user_like')
        ]
        indexes = [
            models.Index(fields=['post', 'user']),
        ]

    def __str__(self):
        return f"@{self.user.username} liked Post #{self.post_id}"


class Follow(models.Model):
    """
    Self-referential Follow model linking followers to users they follow.
    Guarantees unique relationship and prevents self-following.
    """
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'following'], name='unique_follower_following'),
            models.CheckConstraint(
                condition=~Q(follower=F('following')),
                name='prevent_self_follow'
            )
        ]
        indexes = [
            models.Index(fields=['follower', 'following']),
        ]

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Users cannot follow themselves.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"@{self.follower.username} follows @{self.following.username}"


class Notification(models.Model):
    """
    In-app Notification model notifying users of new likes, comments, and followers.
    """
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for @{self.recipient.username}: {self.notification_type} from @{self.sender.username}"
