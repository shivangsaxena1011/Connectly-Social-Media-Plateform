from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator

from .models import Profile, Post, Comment, Like, Follow, Notification
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    UserUpdateForm,
    ProfileUpdateForm,
    PostForm,
    CommentForm
)


# ==========================================
# Authentication Views
# ==========================================

def register_view(request):
    """Register a new user account."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Log the user in immediately after registering
            login(request, user)
            messages.success(request, f"Welcome to Connectly, @{user.username}!")
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Log in existing user."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, @{user.username}!")
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'registration/login.html', {'form': form})


@login_required
def logout_view(request):
    """Log out current user."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ==========================================
# Core Feed & Social Timeline
# ==========================================

@login_required
def feed_view(request):
    """
    Main home feed.
    Supports 'for_you' (global active feed) and 'following' (posts from users followed).
    Includes in-timeline post creator, trending tags, and suggested users.
    """
    feed_filter = request.GET.get('tab', 'for_you')
    user = request.user

    active_comments_prefetch = Prefetch(
        'comments',
        queryset=Comment.objects.filter(is_deleted=False).select_related('user', 'user__profile')
    )

    if feed_filter == 'following':
        following_ids = user.following.values_list('following_id', flat=True)
        posts_qs = Post.objects.filter(
            Q(user_id__in=following_ids) | Q(user=user)
        ).select_related('user', 'user__profile').prefetch_related('likes', active_comments_prefetch)
    else:
        posts_qs = Post.objects.all().select_related('user', 'user__profile').prefetch_related('likes', active_comments_prefetch)

    # Paginate posts (10 per page)
    paginator = Paginator(posts_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Post composer form
    post_form = PostForm()
    comment_form = CommentForm()

    # Suggested users to follow (excluding self and already followed users)
    already_following = user.following.values_list('following_id', flat=True)
    suggested_users = User.objects.exclude(id=user.id).exclude(id__in=already_following).select_related('profile')[:5]

    # Trending tags placeholder / mockup
    trending_topics = [
        {'tag': '#TechTrends', 'posts_count': 1420},
        {'tag': '#WebDev', 'posts_count': 982},
        {'tag': '#AIInnovation', 'posts_count': 756},
        {'tag': '#DesignSystems', 'posts_count': 512},
    ]

    context = {
        'page_obj': page_obj,
        'feed_filter': feed_filter,
        'post_form': post_form,
        'comment_form': comment_form,
        'suggested_users': suggested_users,
        'trending_topics': trending_topics,
    }
    return render(request, 'social/feed.html', context)


# ==========================================
# Explore & Discovery
# ==========================================

@login_required
def explore_view(request):
    """
    Explore page for discovering creators and popular posts.
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('cat', 'all')

    posts_qs = Post.objects.all().select_related('user', 'user__profile').prefetch_related('likes', 'comments')

    if query:
        posts_qs = posts_qs.filter(
            Q(content__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query)
        )

    # Order explore posts by popularity (likes count)
    posts_qs = posts_qs.annotate(like_total=Count('likes')).order_by('-like_total', '-created_at')

    # Suggested creators
    already_following = request.user.following.values_list('following_id', flat=True)
    creators = User.objects.exclude(id=request.user.id).select_related('profile').annotate(
        followers_count=Count('followers')
    ).order_by('-followers_count')[:6]

    context = {
        'posts': posts_qs[:20],
        'creators': creators,
        'query': query,
        'category': category,
        'already_following': list(already_following),
    }
    return render(request, 'social/explore.html', context)


# ==========================================
# User Profiles & Follow System
# ==========================================

@login_required
def profile_view(request, username):
    """
    Display public user profile with posts, likes, follower counts, and interaction buttons.
    """
    profile_user = get_object_or_404(User.objects.select_related('profile'), username=username)
    active_tab = request.GET.get('tab', 'posts')

    is_self = (request.user == profile_user)
    is_following = False
    if not is_self:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    # Counts
    posts_count = profile_user.posts.count()
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    if active_tab == 'likes':
        liked_post_ids = profile_user.likes.values_list('post_id', flat=True)
        posts = Post.objects.filter(id__in=liked_post_ids).select_related('user', 'user__profile')
    elif active_tab == 'media':
        posts = profile_user.posts.exclude(image='').exclude(image__isnull=True).select_related('user', 'user__profile')
    else:
        posts = profile_user.posts.all().select_related('user', 'user__profile')

    comment_form = CommentForm()

    context = {
        'profile_user': profile_user,
        'is_self': is_self,
        'is_following': is_following,
        'posts_count': posts_count,
        'followers_count': followers_count,
        'following_count': following_count,
        'posts': posts,
        'active_tab': active_tab,
        'comment_form': comment_form,
    }
    return render(request, 'social/profile.html', context)


@login_required
def profile_edit_view(request):
    """
    Allows the logged-in user to update their bio, profile photo, website, location, and name.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'social/profile_edit.html', context)


@login_required
def followers_list_view(request, username):
    """Lists all followers of a user."""
    profile_user = get_object_or_404(User, username=username)
    followers = profile_user.followers.select_related('follower', 'follower__profile')
    following_ids = set(request.user.following.values_list('following_id', flat=True))

    context = {
        'profile_user': profile_user,
        'users_list': [f.follower for f in followers],
        'list_type': 'Followers',
        'my_following': following_ids,
    }
    return render(request, 'social/followers_list.html', context)


@login_required
def following_list_view(request, username):
    """Lists all users followed by a user."""
    profile_user = get_object_or_404(User, username=username)
    following = profile_user.following.select_related('following', 'following__profile')
    following_ids = set(request.user.following.values_list('following_id', flat=True))

    context = {
        'profile_user': profile_user,
        'users_list': [f.following for f in following],
        'list_type': 'Following',
        'my_following': following_ids,
    }
    return render(request, 'social/followers_list.html', context)


@login_required
@require_POST
def follow_toggle_view(request, username):
    """
    Follow or unfollow a user.
    Returns JSON for AJAX or redirects for regular POST.
    """
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)
        messages.warning(request, "You cannot follow yourself.")
        return redirect('profile', username=username)

    follow_record = Follow.objects.filter(follower=request.user, following=target_user).first()

    if follow_record:
        follow_record.delete()
        is_following = False
        action = "unfollowed"
    else:
        Follow.objects.create(follower=request.user, following=target_user)
        is_following = True
        action = "followed"

    followers_count = target_user.followers.count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_following': is_following,
            'followers_count': followers_count,
            'action': action,
            'username': target_user.username,
        })

    messages.info(request, f"You {action} @{target_user.username}.")
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('profile', username=username)


# ==========================================
# Post CRUD Operations
# ==========================================

@login_required
def post_create_view(request):
    """
    Handles creating a new post (text + optional image).
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Your post is now live!")
            return redirect('home')
        else:
            messages.error(request, "Please provide valid post content.")
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return redirect(referer)
            return redirect('home')
    else:
        form = PostForm()

    return render(request, 'social/post_form.html', {'form': form, 'title': 'Create Post'})


@login_required
def post_detail_view(request, pk):
    """
    Shows full post detail and comments thread.
    """
    post = get_object_or_404(
        Post.objects.select_related('user', 'user__profile').prefetch_related('comments', 'likes'),
        pk=pk,
        is_deleted=False
    )
    comments = post.comments.filter(is_deleted=False).select_related('user', 'user__profile')
    comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'social/post_detail.html', context)


@login_required
def post_edit_view(request, pk):
    """
    Edit existing post (only by author).
    """
    post = get_object_or_404(Post, pk=pk, is_deleted=False)
    if post.user != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'social/post_form.html', {'form': form, 'title': 'Edit Post', 'post': post})


@login_required
@require_POST
def post_delete_view(request, pk):
    """
    Soft-delete post (only by author).
    """
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    post.is_deleted = True
    post.save()
    messages.success(request, "Post deleted successfully.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'post_id': pk})
    return redirect('home')


# ==========================================
# Likes & Comments (with AJAX support)
# ==========================================

@login_required
@require_POST
def like_toggle_view(request, pk):
    """
    Like or unlike a post.
    """
    post = get_object_or_404(Post, pk=pk, is_deleted=False)
    like_obj = Like.objects.filter(post=post, user=request.user).first()

    if like_obj:
        like_obj.delete()
        is_liked = False
    else:
        Like.objects.create(post=post, user=request.user)
        is_liked = True

    likes_count = post.likes.count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'likes_count': likes_count,
            'post_id': pk
        })

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('home')


@login_required
@require_POST
def comment_add_view(request, pk):
    """
    Add a comment to a post.
    """
    post = get_object_or_404(Post, pk=pk, is_deleted=False)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            avatar = request.user.profile.avatar_url
            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'username': request.user.username,
                'display_name': request.user.profile.display_name,
                'avatar_url': avatar,
                'content': comment.content,
                'created_at': "Just now",
                'comments_count': post.comments_count,
            })

        messages.success(request, "Comment posted!")
    else:
        messages.error(request, "Comment content cannot be empty.")

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('post_detail', pk=pk)


@login_required
@require_POST
def comment_delete_view(request, pk):
    """
    Delete a comment (by comment author or post owner).
    """
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user and comment.post.user != request.user:
        return HttpResponseForbidden("Not authorized to delete this comment.")

    comment.is_deleted = True
    comment.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'comment_id': pk,
            'comments_count': comment.post.comments_count
        })

    messages.success(request, "Comment removed.")
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('post_detail', pk=comment.post.pk)


# ==========================================
# Notifications & Search
# ==========================================

@login_required
def notifications_view(request):
    """
    View user notifications and mark them as read.
    """
    notifications = request.user.notifications.all().select_related('sender', 'sender__profile', 'post')[:50]
    # Mark unread as read
    request.user.notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'social/notifications.html', {'notifications': notifications})


@login_required
def search_view(request):
    """
    Search users and posts.
    """
    query = request.GET.get('q', '').strip()
    users = []
    posts = []

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).select_related('profile')[:10]

        posts = Post.objects.filter(
            content__icontains=query
        ).select_related('user', 'user__profile').prefetch_related('likes', 'comments')[:20]

    context = {
        'query': query,
        'users': users,
        'posts': posts,
    }
    return render(request, 'social/search_results.html', context)
