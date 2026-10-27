/**
 * Connectly - Core Client JavaScript Application
 * Handles AJAX interactions for Likes, Comments, Follows, Modals, and Toasts.
 */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Toast Notification Manager
function showToast(message, type = 'success') {
    const toast = document.getElementById('appToast');
    const toastMsg = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');

    if (!toast) return;

    toastMsg.textContent = message;
    if (type === 'success') {
        toast.className = 'fixed top-5 right-5 z-50 flex items-center gap-3 bg-slate-900 text-white px-5 py-3 rounded-2xl shadow-xl transition-all duration-300 toast-show border border-slate-700';
        toastIcon.textContent = 'check_circle';
        toastIcon.className = 'material-symbols-outlined text-emerald-400 text-xl';
    } else if (type === 'error') {
        toast.className = 'fixed top-5 right-5 z-50 flex items-center gap-3 bg-red-950 text-white px-5 py-3 rounded-2xl shadow-xl transition-all duration-300 toast-show border border-red-800';
        toastIcon.textContent = 'error';
        toastIcon.className = 'material-symbols-outlined text-rose-400 text-xl';
    } else {
        toast.className = 'fixed top-5 right-5 z-50 flex items-center gap-3 bg-indigo-950 text-white px-5 py-3 rounded-2xl shadow-xl transition-all duration-300 toast-show border border-indigo-800';
        toastIcon.textContent = 'info';
        toastIcon.className = 'material-symbols-outlined text-indigo-400 text-xl';
    }

    setTimeout(() => {
        toast.classList.remove('toast-show');
        toast.classList.add('opacity-0', 'pointer-events-none');
    }, 3500);
}

// Like/Unlike Toggle via AJAX
function toggleLike(postId, btnElement) {
    const url = `/post/${postId}/like/`;
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const countEl = btnElement.querySelector('.like-count');
            const iconEl = btnElement.querySelector('.like-icon');

            if (countEl) countEl.textContent = data.likes_count;
            if (iconEl) {
                iconEl.classList.add('heart-animate');
                setTimeout(() => iconEl.classList.remove('heart-animate'), 300);

                if (data.is_liked) {
                    iconEl.classList.remove('text-slate-500');
                    iconEl.classList.add('text-rose-500');
                    iconEl.style.fontVariationSettings = "'FILL' 1";
                } else {
                    iconEl.classList.remove('text-rose-500');
                    iconEl.classList.add('text-slate-500');
                    iconEl.style.fontVariationSettings = "'FILL' 0";
                }
            }
        }
    })
    .catch(err => {
        console.error('Error toggling like:', err);
    });
}

// Follow/Unfollow Toggle via AJAX
function toggleFollow(username, btnElement) {
    const url = `/follow/${username}/`;
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const textEl = btnElement.querySelector('.follow-text') || btnElement;
            const countEl = document.getElementById(`followers-count-${username}`) || document.getElementById('profile-followers-count');

            if (countEl) countEl.textContent = data.followers_count;

            if (data.is_following) {
                textEl.textContent = 'Following';
                btnElement.classList.remove('bg-[#4648d4]', 'text-white', 'hover:bg-indigo-700');
                btnElement.classList.add('bg-slate-100', 'text-slate-700', 'hover:bg-slate-200');
                showToast(`You are now following @${username}`);
            } else {
                textEl.textContent = 'Follow';
                btnElement.classList.remove('bg-slate-100', 'text-slate-700', 'hover:bg-slate-200');
                btnElement.classList.add('bg-[#4648d4]', 'text-white', 'hover:bg-indigo-700');
                showToast(`Unfollowed @${username}`, 'info');
            }
        }
    })
    .catch(err => {
        console.error('Error toggling follow:', err);
    });
}

// AJAX Comment Submission
function submitComment(event, postId) {
    event.preventDefault();
    const form = event.target;
    const input = form.querySelector('input[name="content"]');
    const content = input.value.trim();

    if (!content) return;

    const formData = new FormData(form);

    fetch(`/post/${postId}/comment/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            input.value = '';
            // Update comments count on post
            const countEl = document.querySelector(`.post-comments-count-${postId}`);
            if (countEl) countEl.textContent = data.comments_count;

            // Append comment to thread
            const commentsContainer = document.getElementById(`comments-list-${postId}`);
            if (commentsContainer) {
                const commentHTML = `
                    <div id="comment-${data.comment_id}" class="flex items-start gap-3 text-sm py-2 group">
                        <img src="${data.avatar_url}" class="w-7 h-7 rounded-full object-cover mt-0.5 border border-slate-200" alt="${data.username}">
                        <div class="flex-1 bg-slate-50 rounded-2xl px-3.5 py-2">
                            <div class="flex items-center justify-between">
                                <span class="font-semibold text-slate-900">${data.display_name}</span>
                                <span class="text-xs text-slate-400">${data.created_at}</span>
                            </div>
                            <p class="text-slate-700 mt-0.5">${data.content}</p>
                        </div>
                    </div>
                `;
                commentsContainer.insertAdjacentHTML('beforeend', commentHTML);
            }
            showToast('Comment posted!');
        }
    })
    .catch(err => {
        console.error('Error submitting comment:', err);
    });
}

// Image Preview Utility
function setupImagePreview(inputId, previewContainerId, previewImgId) {
    const input = document.getElementById(inputId);
    const container = document.getElementById(previewContainerId);
    const img = document.getElementById(previewImgId);

    if (!input || !container || !img) return;

    input.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                img.src = e.target.result;
                container.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    });
}

function removePreview(inputId, containerId) {
    const input = document.getElementById(inputId);
    const container = document.getElementById(containerId);
    if (input) input.value = '';
    if (container) container.classList.add('hidden');
}

// Modal open & close
function openPostModal() {
    const modal = document.getElementById('createPostModal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
}

function closePostModal() {
    const modal = document.getElementById('createPostModal');
    if (modal) {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }
}
