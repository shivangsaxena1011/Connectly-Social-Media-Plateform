from django.contrib import admin
from .models import Profile, Post, Comment, Like, Follow, Notification


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'website', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    list_filter = ('created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_snippet', 'likes_count', 'comments_count', 'created_at', 'is_deleted')
    search_fields = ('user__username', 'content')
    list_filter = ('is_deleted', 'created_at')
    actions = ['soft_delete', 'restore']

    def content_snippet(self, obj):
        return (obj.content[:40] + '...') if len(obj.content) > 40 else obj.content

    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
    soft_delete.short_description = "Soft delete selected posts"

    def restore(self, request, queryset):
        queryset.update(is_deleted=False)
    restore.short_description = "Restore selected posts"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'content_snippet', 'created_at', 'is_deleted')
    search_fields = ('user__username', 'content')
    list_filter = ('is_deleted', 'created_at')

    def content_snippet(self, obj):
        return (obj.content[:30] + '...') if len(obj.content) > 30 else obj.content


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    search_fields = ('user__username', 'post__content')
    list_filter = ('created_at',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'sender', 'notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username')
    list_filter = ('notification_type', 'is_read', 'created_at')
