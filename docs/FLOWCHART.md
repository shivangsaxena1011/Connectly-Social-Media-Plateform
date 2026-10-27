# Connectly - Social Media Application Flowchart

![App Flowchart](images/Connectly%20Social%20Media%20App%20Flowchart.png)

## Core User Journeys

### 1. Registration & Login Flow
1. User visits `/register/` or `/login/`.
2. User provides credentials:
   - On Registration: Email and username uniqueness checked; passwords validated. Profile created automatically via post-save signal.
   - On Login: Authenticated against Django's hashed password store.
3. Successful login redirects user directly to the Home Feed (`/`).

---

### 2. Home Feed Flow
1. User lands on `/` (Home Feed).
2. Feed retrieves active, non-deleted posts with author profile and like states pre-fetched.
3. User toggles between:
   - **For You:** Global community timeline.
   - **Following:** Curated posts exclusively from accounts the user follows.
4. User can create new posts directly from the in-feed composer or top modal.

---

### 3. Post Interaction Flow (Likes & Comments)
1. **Like Toggle:**
   - User clicks heart icon on post card.
   - JavaScript sends `POST` request with CSRF token to `/post/<id>/like/`.
   - Backend creates or deletes `Like` record within database transaction.
   - Response returns updated count and state; button triggers bounce animation and color fill.
2. **Comment Posting:**
   - User enters text in comment input and presses Enter or Reply.
   - JavaScript sends AJAX request to `/post/<id>/comment/`.
   - Comment is saved; response returns comment author details and rendered HTML.
   - New comment instantly prepends/appends to thread without page refresh.

---

### 4. Follow / Unfollow Flow
1. User clicks "Follow" on a user card or profile page.
2. Request sent to `/follow/<username>/`.
3. Self-follow check performed (forbidden if `follower == following`).
4. Relationship toggled; follower count synchronized across active UI.

---

### 5. Profile Management Flow
1. User accesses `/profile/<username>/`.
2. Public profile presents banner, avatar, bio, location, website, and statistics.
3. User selects tabs:
   - **Posts:** Chronological list of user's posts.
   - **Media:** Posts containing photos.
   - **Likes:** Posts liked by this user.
4. If visiting own profile, user can click "Edit Profile" (`/profile/edit/`) to update their bio, location, website, or upload a new avatar.
