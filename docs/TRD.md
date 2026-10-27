# Connectly - Technical Requirements Document (TRD)

![Connectly TRD Infographic](images/Connectly%20Social%20Media%20TRD%20Infographic.png)

## 1. System Overview

Connectly is architected using Django's Model-View-Template (MVT) pattern, paired with a lightweight client-side layer (vanilla JavaScript + Tailwind CSS) to deliver high-performance AJAX interactions without the complexity of a heavy SPA framework.

- **Backend Framework:** Django (Python 3.14+)
- **Database:** SQLite (Development) / PostgreSQL (Production)
- **Frontend:** HTML5, Tailwind CSS (via CDN), Google Fonts, Material Symbols Outlined
- **Scripting:** Vanilla JavaScript (ES6+) with Fetch API and CSRF protection
- **Image Processing:** Pillow (PIL) for image verification and thumbnails

---

## 2. High-Level Architecture

```
[ Web Browser (Desktop / Mobile) ]
           │
           │  HTTPS / HTTP
           ▼
[ Django Application Router (connectly/urls.py) ]
           │
           ▼
[ Social View Handlers (social/views.py) ]
   ├── Authentication & Sessions
   ├── Query Optimization (select_related, prefetch_related)
   ├── Permission Verification
   └── Response Generation (HTML Templates / JSON APIs)
           │
           ├──► [ Database Layer (Django ORM ➔ SQLite / PostgreSQL) ]
           └──► [ Media Storage (/media/posts/, /media/profiles/) ]
```

---

## 3. Database Schema & ER Model

![Backend Schema Infographic](images/Connectly%20Backend%20Schema%20Infographic.png)

### Key Entities:
1. **User (`auth_user`):**
   - Built-in Django auth user (`id`, `username`, `email`, `password`, `first_name`, `last_name`, `is_active`, `date_joined`).
2. **Profile (`social_profile`):**
   - Extended user metadata (`id`, `user_id`, `bio`, `profile_picture`, `website`, `location`, `created_at`, `updated_at`).
   - One-to-One relationship with `auth_user`.
3. **Post (`social_post`):**
   - User content (`id`, `user_id`, `content`, `image`, `created_at`, `updated_at`, `is_deleted`).
   - Filtered with custom manager `ActivePostManager` (`is_deleted=False`).
4. **Comment (`social_comment`):**
   - Discussion records (`id`, `post_id`, `user_id`, `content`, `created_at`, `updated_at`, `is_deleted`).
5. **Like (`social_like`):**
   - Like ledger (`id`, `post_id`, `user_id`, `created_at`).
   - Unique constraint: `(post_id, user_id)`.
6. **Follow (`social_follow`):**
   - Follower ledger (`id`, `follower_id`, `following_id`, `created_at`).
   - Unique constraint: `(follower_id, following_id)`.
   - Check constraint: `follower_id != following_id`.
7. **Notification (`social_notification`):**
   - Activity notifications (`id`, `recipient_id`, `sender_id`, `notification_type`, `post_id`, `is_read`, `created_at`).

---

## 4. API & URL Endpoints Specification

| Endpoint | Method | View Function | Description |
|---|---|---|---|
| `/` | GET | `feed_view` | Home feed (supports `?tab=for_you` and `?tab=following`) |
| `/register/` | GET, POST | `register_view` | User account registration |
| `/login/` | GET, POST | `login_view` | User session authentication |
| `/logout/` | GET, POST | `logout_view` | User session termination |
| `/explore/` | GET | `explore_view` | Explore & discover posts/creators (`?q=`, `?cat=`) |
| `/profile/<username>/` | GET | `profile_view` | Public user profile with tabs (`posts`, `media`, `likes`) |
| `/profile/edit/` | GET, POST | `profile_edit_view` | Current user profile editor |
| `/profile/<username>/followers/` | GET | `followers_list_view` | List of followers for a user |
| `/profile/<username>/following/` | GET | `following_list_view` | List of users followed by a user |
| `/follow/<username>/` | POST | `follow_toggle_view` | Toggle follow/unfollow (AJAX JSON / redirect) |
| `/post/create/` | GET, POST | `post_create_view` | Create post (multipart form text + image) |
| `/post/<id>/` | GET | `post_detail_view` | Post detail view with full comments thread |
| `/post/<id>/edit/` | GET, POST | `post_edit_view` | Edit existing post (author-only) |
| `/post/<id>/delete/` | POST | `post_delete_view` | Soft-delete post (author-only) |
| `/post/<id>/like/` | POST | `like_toggle_view` | Toggle post like/unlike (AJAX JSON / redirect) |
| `/post/<id>/comment/` | POST | `comment_add_view` | Submit post comment (AJAX JSON / redirect) |
| `/comment/<id>/delete/` | POST | `comment_delete_view` | Soft-delete comment (author/owner-only) |
| `/notifications/` | GET | `notifications_view` | In-app notifications list |
| `/search/` | GET | `search_view` | Full-text keyword search for users & posts |

---

## 5. Security & Performance Considerations

### Security Measures:
- **CSRF Protection:** Django's `CsrfViewMiddleware` enforces CSRF tokens across all form submissions and AJAX calls (read from cookie via JavaScript).
- **Password Hashing:** Passwords encrypted via PBKDF2 with SHA-256 by default.
- **Strict Authorization:** Post and comment mutations check `request.user == object.user` before allowing edits or deletions.
- **SQL Injection Prevention:** 100% ORM parameterized queries.
- **Self-Follow Prevention:** Enforced at both the Django model clean method and the database check constraint level.

### Performance Optimizations:
- **N+1 Query Elimination:** All list views employ `select_related('user', 'user__profile')` and `prefetch_related('likes', 'comments')`.
- **Database Indexes:** Compound indexes on `(user, -created_at)`, `(is_deleted, -created_at)`, `(post, created_at)`, `(follower, following)`, and `(post, user)`.
- **Pagination:** Feed queries use Django's `Paginator` to bound result sets to 10 items per page.
