from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Profile, Post, Comment, Like, Follow, Notification


class ConnectlyModelTests(TestCase):
    """Unit tests for Connectly models, relationships, and constraints."""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='shivang',
            email='shivang@example.com',
            password='testpassword123',
            first_name='Shivang',
            last_name='Saxena'
        )
        self.user2 = User.objects.create_user(
            username='ananya',
            email='ananya@example.com',
            password='testpassword123',
            first_name='Ananya',
            last_name='Sharma'
        )

    def test_profile_auto_created_on_user_registration(self):
        """Verify that user profile is automatically created by signals."""
        self.assertIsNotNone(self.user1.profile)
        self.assertEqual(self.user1.profile.user, self.user1)
        self.assertEqual(self.user1.profile.display_name, 'Shivang Saxena')

    def test_post_creation_and_soft_delete(self):
        """Verify post creation and soft-delete filtering."""
        post = Post.objects.create(user=self.user1, content="Hello Connectly!")
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.likes_count, 0)
        self.assertEqual(post.comments_count, 0)

        # Soft delete
        post.is_deleted = True
        post.save()
        self.assertEqual(Post.objects.count(), 0)  # default manager excludes soft deleted
        self.assertEqual(Post.all_objects.count(), 1)

    def test_like_system_and_unique_constraint(self):
        """Verify like creation and prevention of duplicate likes."""
        post = Post.objects.create(user=self.user1, content="Test post for likes")
        like1 = Like.objects.create(user=self.user2, post=post)
        self.assertEqual(post.likes_count, 1)

        # Attempting duplicate like should raise integrity error / validation
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Like.objects.create(user=self.user2, post=post)

    def test_follow_system_and_prevent_self_follow(self):
        """Verify following another user and prevention of self-following."""
        # Valid follow
        follow = Follow.objects.create(follower=self.user1, following=self.user2)
        self.assertEqual(self.user2.followers.count(), 1)
        self.assertEqual(self.user1.following.count(), 1)

        # Prevent duplicate follow
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Follow.objects.create(follower=self.user1, following=self.user2)

        # Prevent self-follow
        with self.assertRaises(ValidationError):
            self_follow = Follow(follower=self.user1, following=self.user1)
            self_follow.save()

    def test_comment_system(self):
        """Verify adding and soft deleting comments."""
        post = Post.objects.create(user=self.user1, content="Comment on me")
        comment = Comment.objects.create(post=post, user=self.user2, content="Awesome post!")
        self.assertEqual(post.comments_count, 1)

        comment.is_deleted = True
        comment.save()
        self.assertEqual(post.comments_count, 0)


class ConnectlyViewTests(TestCase):
    """Integration tests for views, authentication, and AJAX interactions."""

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='shivang',
            email='shivang@example.com',
            password='Password123!',
            first_name='Shivang'
        )
        self.user2 = User.objects.create_user(
            username='rahul',
            email='rahul@example.com',
            password='Password123!',
            first_name='Rahul'
        )
        self.post = Post.objects.create(user=self.user1, content="Community update!")

    def test_feed_requires_login(self):
        """Unauthenticated access redirects to login."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_feed_authenticated_access(self):
        """Authenticated user can view feed."""
        self.client.login(username='shivang', password='Password123!')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Community update!")

    def test_ajax_like_toggle(self):
        """Test liking and unliking via AJAX."""
        self.client.login(username='rahul', password='Password123!')
        url = reverse('post_like', kwargs={'pk': self.post.pk})

        # First like
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_liked'])
        self.assertEqual(data['likes_count'], 1)

        # Unlike
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertFalse(data['is_liked'])
        self.assertEqual(data['likes_count'], 0)

    def test_ajax_follow_toggle(self):
        """Test follow and unfollow via AJAX."""
        self.client.login(username='rahul', password='Password123!')
        url = reverse('follow_toggle', kwargs={'username': 'shivang'})

        # Follow
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_following'])
        self.assertEqual(data['followers_count'], 1)

        # Unfollow
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertFalse(data['is_following'])
        self.assertEqual(data['followers_count'], 0)

    def test_ajax_comment_add(self):
        """Test adding comment via AJAX."""
        self.client.login(username='rahul', password='Password123!')
        url = reverse('post_comment', kwargs={'pk': self.post.pk})
        response = self.client.post(
            url,
            {'content': 'Looking great!'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['content'], 'Looking great!')
        self.assertEqual(data['comments_count'], 1)

    def test_post_delete_permission(self):
        """User cannot delete another user's post."""
        self.client.login(username='rahul', password='Password123!')
        url = reverse('post_delete', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.post.refresh_from_db()
        self.assertFalse(self.post.is_deleted)

    def test_login_with_email(self):
        """User can log in using their email address instead of username."""
        response = self.client.post(reverse('login'), {
            'username': 'shivang@example.com',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_comment_delete_with_referer(self):
        """Deleting a comment with HTTP_REFERER header redirects properly without TypeError."""
        comment = Comment.objects.create(post=self.post, user=self.user2, content="Nice update")
        self.client.login(username='rahul', password='Password123!')
        url = reverse('comment_delete', kwargs={'pk': comment.pk})
        referer_url = f"/post/{self.post.pk}/"
        response = self.client.post(url, HTTP_REFERER=referer_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, referer_url)
        comment.refresh_from_db()
        self.assertTrue(comment.is_deleted)

    def test_unread_notifications_property(self):
        """Profile.unread_notifications_count returns accurate number of unread alerts."""
        self.assertEqual(self.user1.profile.unread_notifications_count, 0)
        Notification.objects.create(
            recipient=self.user1,
            sender=self.user2,
            notification_type='follow'
        )
        self.assertEqual(self.user1.profile.unread_notifications_count, 1)
