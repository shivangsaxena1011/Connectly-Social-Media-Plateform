"""
Database Seeder Script for Connectly Social Media Platform.
Populates realistic demo users, profile details, sample avatars, post images,
likes, comments, and follow relationships matching the project TRD, PRD, and design mockups.
"""

import os
import sys
import django

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectly.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from social.models import Profile, Post, Comment, Like, Follow
from PIL import Image, ImageDraw, ImageFont
import io


def create_avatar(text, bg_color):
    """Generate a clean colored circle avatar with user initials."""
    img = Image.new('RGB', (256, 256), color=bg_color)
    draw = ImageDraw.Draw(img)
    # Circle outline
    draw.ellipse([10, 10, 246, 246], outline=(255, 255, 255, 80), width=6)
    # Draw simple initial or graphic
    draw.ellipse([70, 50, 186, 166], fill=(255, 255, 255, 220))
    draw.ellipse([30, 180, 226, 320], fill=(255, 255, 255, 220))

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=90)
    return ContentFile(buf.getvalue())


def create_post_image(title, subtitle, gradient_colors):
    """Generate sample media post image."""
    img = Image.new('RGB', (800, 500), color=gradient_colors[0])
    draw = ImageDraw.Draw(img)

    # Simple geometric gradient-like pattern
    for y in range(0, 500, 4):
        ratio = y / 500.0
        r = int(gradient_colors[0][0] * (1 - ratio) + gradient_colors[1][0] * ratio)
        g = int(gradient_colors[0][1] * (1 - ratio) + gradient_colors[1][1] * ratio)
        b = int(gradient_colors[0][2] * (1 - ratio) + gradient_colors[1][2] * ratio)
        draw.line([(0, y), (800, y)], fill=(r, g, b))

    # Add artistic mountain silhouette
    mountain_points = [
        (0, 500), (0, 360), (120, 240), (220, 320),
        (380, 160), (520, 310), (660, 200), (800, 330), (800, 500)
    ]
    draw.polygon(mountain_points, fill=(24, 30, 54))

    # Sun / Moon
    draw.ellipse([580, 70, 680, 170], fill=(255, 215, 0))

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return ContentFile(buf.getvalue())


def seed():
    print("🌱 Starting Connectly database seeding...")

    # 1. Create Demo Users
    demo_users_data = [
        {
            'username': 'shivang',
            'first_name': 'Shivang',
            'last_name': 'Saxena',
            'email': 'shivang@connectly.app',
            'password': 'connectly123',
            'bio': 'Passionate about technology, AI and building cool web platforms. 🚀 Founder & Lead Developer.',
            'location': 'Bangalore, India',
            'website': 'https://github.com/shivangsaxena1011',
            'bg_color': (70, 72, 212),
            'is_superuser': True,
        },
        {
            'username': 'ananya',
            'first_name': 'Ananya',
            'last_name': 'Sharma',
            'email': 'ananya@connectly.app',
            'password': 'connectly123',
            'bio': 'Product designer & creative technologist. Designing intuitive digital experiences. ✨',
            'location': 'Mumbai, India',
            'website': 'https://ananya.design',
            'bg_color': (236, 72, 153),
            'is_superuser': False,
        },
        {
            'username': 'rahul',
            'first_name': 'Rahul',
            'last_name': 'Verma',
            'email': 'rahul@connectly.app',
            'password': 'connectly123',
            'bio': 'Full-stack explorer & open source enthusiast. Exploring Django, Python, and cloud systems. 💻',
            'location': 'New Delhi, India',
            'website': 'https://rahulverma.dev',
            'bg_color': (16, 185, 129),
            'is_superuser': False,
        },
        {
            'username': 'priya',
            'first_name': 'Priya',
            'last_name': 'Patel',
            'email': 'priya@connectly.app',
            'password': 'connectly123',
            'bio': 'Travel photographer & storyteller. Capturing everyday moments and scenic horizons. 📷',
            'location': 'Goa, India',
            'website': 'https://priyapatel.photography',
            'bg_color': (245, 158, 11),
            'is_superuser': False,
        },
        {
            'username': 'alex',
            'first_name': 'Alex',
            'last_name': 'Chen',
            'email': 'alex@connectly.app',
            'password': 'connectly123',
            'bio': 'Software Architect. Coffee, distributed databases, and high-performance APIs. ☕',
            'location': 'San Francisco, CA',
            'website': 'https://alexchen.io',
            'bg_color': (99, 102, 241),
            'is_superuser': False,
        }
    ]

    users = {}
    for data in demo_users_data:
        user, created = User.objects.get_or_create(username=data['username'])
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.is_superuser = data['is_superuser']
        user.is_staff = data['is_superuser']
        user.set_password(data['password'])
        user.save()

        # Update profile
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.bio = data['bio']
        profile.location = data['location']
        profile.website = data['website']
        avatar_file = create_avatar(data['username'], data['bg_color'])
        profile.profile_picture.save(f"{data['username']}_avatar.jpg", avatar_file, save=False)
        profile.save()

        users[data['username']] = user
        print(f"  ✓ User created: @{user.username} ({user.profile.display_name})")

    # 2. Create Follow Relationships
    follows_data = [
        ('shivang', 'ananya'),
        ('shivang', 'rahul'),
        ('shivang', 'priya'),
        ('ananya', 'shivang'),
        ('ananya', 'rahul'),
        ('rahul', 'shivang'),
        ('rahul', 'ananya'),
        ('priya', 'shivang'),
        ('priya', 'ananya'),
        ('alex', 'shivang'),
        ('alex', 'rahul'),
    ]

    for follower_name, following_name in follows_data:
        f_user = users[follower_name]
        t_user = users[following_name]
        Follow.objects.get_or_create(follower=f_user, following=t_user)
    print("  ✓ Created follow relationships.")

    # 3. Create Demo Posts with Images
    mountain_img = create_post_image("Mountains", "Campus View", ((99, 102, 241), (236, 72, 153)))
    sunset_img = create_post_image("Sunset", "Goa Horizons", ((249, 115, 22), (236, 72, 153)))
    workspace_img = create_post_image("Workspace", "Clean Setup", ((16, 185, 129), (59, 130, 246)))

    post1 = Post.objects.create(
        user=users['shivang'],
        content="Beautiful view from my college campus! 🏔️ Working on Connectly backend schema and frontend architecture today. Love the progress so far!"
    )
    post1.image.save('campus_mountains.jpg', mountain_img, save=True)

    post2 = Post.objects.create(
        user=users['ananya'],
        content="Productive day! ✨ Refining the Vibrant Connection design system for Connectly. Crisp borders, friendly pill buttons, and high-contrast typography make social feeds so much more enjoyable to browse."
    )
    post2.image.save('design_system.jpg', workspace_img, save=True)

    post3 = Post.objects.create(
        user=users['rahul'],
        content="Loving Django's ORM and clean signal system. Setting up automatic profile generation and follower notifications was a breeze! What's everyone working on this week? 💻"
    )

    post4 = Post.objects.create(
        user=users['priya'],
        content="Golden hour serenity by the sea. 🌅 Always take time to disconnect and recharge with nature between coding sessions."
    )
    post4.image.save('golden_hour.jpg', sunset_img, save=True)

    post5 = Post.objects.create(
        user=users['alex'],
        content="Clean architectures scale best when normalized schemas and indexes are established early on. Great to see Connectly's solid database foundation!"
    )
    print("  ✓ Created sample posts.")

    # 4. Create Likes
    likes_data = [
        (post1, users['ananya']),
        (post1, users['rahul']),
        (post1, users['priya']),
        (post1, users['alex']),
        (post2, users['shivang']),
        (post2, users['rahul']),
        (post3, users['shivang']),
        (post4, users['shivang']),
        (post4, users['ananya']),
    ]
    for p, u in likes_data:
        Like.objects.get_or_create(post=p, user=u)
    print("  ✓ Created post likes.")

    # 5. Create Comments
    comments_data = [
        (post1, users['ananya'], "Amazing photo! ❤️ Campus looks breathtaking."),
        (post1, users['rahul'], "Wow! Where is this? 😍 Truly spectacular."),
        (post1, users['priya'], "So beautiful! 🌄 The lighting is magical."),
        (post2, users['shivang'], "The UI looks super crisp! Love the Indigo and Pink accents."),
        (post3, users['alex'], "Django signals combined with Celery or async tasks are a game changer."),
        (post4, users['shivang'], "Incredible capture Priya! 📸"),
    ]
    for p, u, text in comments_data:
        Comment.objects.create(post=p, user=u, content=text)
    print("  ✓ Created sample comments.")

    print("\n🎉 Seeding completed successfully!")
    print("--------------------------------------------------")
    print("Demo Accounts:")
    print("  • Username: shivang  | Password: connectly123  (Superuser)")
    print("  • Username: ananya   | Password: connectly123")
    print("  • Username: rahul    | Password: connectly123")
    print("  • Username: priya    | Password: connectly123")
    print("  • Username: alex     | Password: connectly123")
    print("--------------------------------------------------")


if __name__ == '__main__':
    seed()
