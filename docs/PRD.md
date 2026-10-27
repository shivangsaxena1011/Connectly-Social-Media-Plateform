# Connectly - Product Requirements Document (PRD)

![Connectly PRD Infographic](images/Connectly%20Social%20Media%20PRD%20Infographic.png)

## 1. Product Overview

- **Product Name:** Connectly
- **Product Type:** Web-based Mini Social Media Platform
- **Motto:** Share · Connect · Grow
- **Target Users:** Students, Developers, Tech Enthusiasts, General Users, and Creators
- **Version:** MVP (v1.0)
- **Platforms:** Web (Responsive for Mobile, Tablet, and Desktop)

### Product Description
Connectly is a simple, expressive, and modern web-based social media platform that allows users to create customizable profiles, share text and media updates, like and comment on community posts, and follow friends and creators. It delivers a fast, clutter-free space designed for meaningful social engagement.

---

## 2. Goals & Objectives

### Primary Goal
Build a fully functional, scalable, and responsive social media platform with core social features (user profiles, chronological timeline feeds, interactive comments, like mechanisms, and follow systems).

### Secondary Goals
- **Clean & Tactile UI/UX:** Provide an intuitive, distraction-free interface built upon the *Vibrant Connection* design system.
- **Robust Security:** Ensure safe session authentication, hashed credentials, CSRF protection, and permission validation.
- **Maintainable Architecture:** Deliver normalized database models, scalable Django ORM patterns, and structured frontend templates.

### Success Metrics
- 100% test pass rate across authentication, models, and AJAX endpoints.
- Sub-second page load speeds on standard broadband connections.
- Zero data integrity violations (guaranteed by database constraints).
- Fluid mobile and desktop responsiveness across screen sizes.

---

## 3. Target User Personas & Use Cases

1. **General Users:**
   - Create and customize a profile with bio, avatar, and social links.
   - Browse the "For You" global feed and interact with community content.
   - Like posts, reply with comments, and share links.

2. **Students & Creators:**
   - Share thoughts, milestone updates, questions, and project screenshots.
   - Build a follower network and curate a personal feed via the "Following" tab.
   - Explore trending topics and discover relevant creators.

3. **Platform Administrators:**
   - Manage users, moderate objectionable posts, and soft-delete flagged items.
   - Inspect database health and activity metrics using the Django Admin panel.

---

## 4. Core Features & Requirements

### A. User Management & Authentication
- Secure user registration with unique username and email validation.
- Login and logout with session persistence and "Remember Me" support.
- User profile auto-creation via post-save Django signals upon registration.
- Profile editing (display name, bio, profile photo, location, website).
- Public profile pages showcasing statistics (Posts count, Followers count, Following count).

### B. Post Management
- Create text posts with optional image attachments.
- Interactive composer in the main feed and dedicated modal dialog.
- Chronological feed ordering (newest posts first).
- Post owner actions: Edit post content and soft-delete post (`is_deleted=True`).
- Dedicated post thread page (`/post/<id>/`) displaying full post media and comments.

### C. Likes & Reactions
- Real-time AJAX like and unlike toggling without page reloading.
- Dynamic like count update and pulse heart animation.
- Database unique constraint preventing multiple likes on the same post by the same user.

### D. Comments System
- Nested comment discussions on each post.
- Instant AJAX comment submission with real-time DOM appending.
- Comment owner and post owner deletion permissions.
- Soft delete support for comment moderation.

### E. Follow System
- Self-referential user follow/unfollow capability.
- Dedicated Followers and Following listing screens.
- Prevention of self-following via model validation and database constraints.
- Separate "Following" feed tab filtering content specifically to followed accounts.

### F. Discovery & Search
- Keyword search covering users (display names, handles) and posts.
- Explore page with category filters (Tech, Design, Photography, Community) and featured creator cards.

---

## 5. Non-Functional Requirements

- **Performance:** Optimized queries using `select_related` and `prefetch_related` to eliminate N+1 queries.
- **Security:** CSRF tokens required on all mutation requests; strict user ownership checks on edit/delete.
- **Usability:** High-contrast typography (Inter + Plus Jakarta Sans), readable fonts, and tactile button feedback.
- **Scalability:** Clean separation of concerns (Model-View-Template pattern), database indexing, and static asset separation.

---

## 6. Future Enhancements
- Direct messaging (DMs) between mutual followers.
- Real-time updates via WebSockets (Django Channels).
- Post bookmarking / saved collections.
- Dark mode theme toggle.
