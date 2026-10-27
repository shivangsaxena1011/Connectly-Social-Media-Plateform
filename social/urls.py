from django.urls import path
from . import views

urlpatterns = [
    # Core Feed & Auth
    path('', views.feed_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('explore/', views.explore_view, name='explore'),

    # Profile & Network
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/followers/', views.followers_list_view, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list_view, name='following_list'),
    path('follow/<str:username>/', views.follow_toggle_view, name='follow_toggle'),

    # Posts & Interactions
    path('post/create/', views.post_create_view, name='post_create'),
    path('post/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('post/<int:pk>/edit/', views.post_edit_view, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete_view, name='post_delete'),
    path('post/<int:pk>/like/', views.like_toggle_view, name='post_like'),
    path('post/<int:pk>/comment/', views.comment_add_view, name='post_comment'),
    path('comment/<int:pk>/delete/', views.comment_delete_view, name='comment_delete'),

    # Notifications & Search
    path('notifications/', views.notifications_view, name='notifications'),
    path('search/', views.search_view, name='search'),
]
