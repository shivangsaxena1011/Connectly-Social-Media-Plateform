from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile, Post, Comment


class UserRegistrationForm(forms.ModelForm):
    """
    Registration form with email uniqueness check and password confirmation.
    """
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] focus:border-transparent text-sm transition',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] focus:border-transparent text-sm transition',
            'placeholder': 'Last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] focus:border-transparent text-sm transition',
            'placeholder': 'name@example.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] focus:border-transparent text-sm transition',
            'placeholder': 'Create strong password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] focus:border-transparent text-sm transition',
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] focus:border-transparent text-sm transition',
                'placeholder': 'Choose username'
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    """
    Styled login form.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] focus:border-transparent text-sm transition',
            'placeholder': 'Username or email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] focus:border-transparent text-sm transition',
            'placeholder': '••••••••'
        })
    )


class UserUpdateForm(forms.ModelForm):
    """
    Form to update standard User attributes.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] text-sm'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] text-sm'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] text-sm'
            }),
        }


class ProfileUpdateForm(forms.ModelForm):
    """
    Form to update Profile details.
    """
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'website', 'location']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] text-sm',
                'rows': 3,
                'placeholder': 'Write a short bio about yourself...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] text-sm',
                'placeholder': 'https://yourwebsite.com'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#4648d4] text-sm',
                'placeholder': 'City, Country'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-[#4648d4] hover:file:bg-indigo-100 cursor-pointer'
            })
        }


class PostForm(forms.ModelForm):
    """
    Form to create or edit a Post.
    """
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full bg-transparent border-0 focus:ring-0 text-slate-800 placeholder-slate-400 text-base resize-none focus:outline-none',
                'rows': 3,
                'placeholder': "What's on your mind? Share updates, ideas, or questions..."
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'post-image-input',
                'accept': 'image/*'
            })
        }


class CommentForm(forms.ModelForm):
    """
    Form to post a comment.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'w-full bg-slate-100 border-0 rounded-full px-4 py-2.5 text-sm text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-[#4648d4] focus:outline-none',
                'placeholder': 'Write a comment...',
                'autocomplete': 'off'
            })
        }
