# Connectly - 7-Day Implementation Roadmap

![Connectly Implementation Roadmap](images/Connectly%20Django%20Implementation%20Roadmap.png)

This roadmap outlines the complete development lifecycle for Connectly, from initial setup to deployment and documentation.

---

### Day 1: Project Setup & Baseline Structure
- [x] Install Python 3.14, Django, and Pillow.
- [x] Set up Django project (`connectly`) and application (`social`).
- [x] Configure base settings (`INSTALLED_APPS`, `TEMPLATES`, `STATICFILES_DIRS`, `MEDIA_ROOT`).
- [x] Establish URL routing structure and modular template inheritance.
- [x] Verify local development server and environment variables.

---

### Day 2: Database Design & Models
- [x] Create normalized database schema:
  - `Profile` (One-to-One with User)
  - `Post` (ForeignKey to User, with soft-delete flag)
  - `Comment` (ForeignKey to Post and User)
  - `Like` (Unique constraint on `post` + `user`)
  - `Follow` (Self-referential with self-follow check constraint)
  - `Notification` (Activity alerts)
- [x] Configure post-save signals for automatic Profile creation and event notifications.
- [x] Create and execute initial migrations.
- [x] Customize Django Admin interface with search, filters, and soft-delete actions.

---

### Day 3: Authentication & User Profiles
- [x] Implement secure registration form with email uniqueness validation and password confirmation.
- [x] Implement login and logout flows with session persistence.
- [x] Build public profile view with dynamic post counters, follower counts, and bio metadata.
- [x] Build profile editing interface for avatar updates, location, and website.
- [x] Add Followers and Following dedicated listing pages.

---

### Day 4: Post Management & Comments System
- [x] Implement post creation form with text and media upload support.
- [x] Display posts chronologically in timeline feeds.
- [x] Build post detail view (`/post/<id>/`) with threaded discussions.
- [x] Implement post edit and soft-delete operations with ownership authorization.
- [x] Implement comment creation and deletion with real-time AJAX DOM insertion.

---

### Day 5: Likes & Follow System
- [x] Implement like/unlike toggle view with JSON response for asynchronous updates.
- [x] Build client-side AJAX handler for instant UI heart pulse animations and counter updates.
- [x] Implement follow/unfollow toggle view with follower count synchronization.
- [x] Build dual-feed system: "For You" (global) vs. "Following" (curated network).
- [x] Create explore page with creator discovery cards and search filtering.

---

### Day 6: Frontend UI & Test Suite
- [x] Apply *Vibrant Connection* design system (Tailwind CSS, Plus Jakarta Sans, Inter).
- [x] Implement responsive 3-column desktop layout and mobile bottom navigation dock.
- [x] Build comprehensive unit and integration test suite (`social/tests.py`).
- [x] Validate model integrity, permissions, CSRF protection, and edge cases (self-follow prevention).
- [x] Pass all 11 test suites with 0 warnings.

---

### Day 7: Documentation, Seeding & Deployment
- [x] Create automated database seeder (`populate_db.py`) with realistic demo creators and posts.
- [x] Embed all 6 high-resolution infographics and UI mockups in repository documentation.
- [x] Write PRD, TRD, Schema, and API specifications.
- [x] Compose comprehensive `README.md` with visual guides, feature checklists, and quickstart commands.
- [x] Initialize Git repository, commit all project artifacts, and push to GitHub.
