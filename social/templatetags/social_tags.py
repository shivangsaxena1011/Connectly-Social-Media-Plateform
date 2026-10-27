from django import template

register = template.Library()


@register.filter
def is_liked_by(post, user):
    """
    Template filter to check if a given user has liked a post.
    Usage: {% if post|is_liked_by:user %}
    """
    if not user or not user.is_authenticated:
        return False
    return post.is_liked_by(user)


@register.filter
def is_following(user, target_user):
    """
    Template filter to check if user follows target_user.
    Usage: {% if user|is_following:target_user %}
    """
    if not user or not user.is_authenticated or user == target_user:
        return False
    return user.following.filter(following=target_user).exists()
