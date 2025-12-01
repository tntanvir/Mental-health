from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the user is saved).
        """
        # If the user exists (is connected), ensure they are active.
        if sociallogin.is_existing:
            user = sociallogin.user
            if not user.is_active:
                user.is_active = True
                user.save()
        
    def save_user(self, request, sociallogin, form=None):
        """
        Invoked when a new user is being created via social signup.
        """
        user = super().save_user(request, sociallogin, form)
        # Ensure new social users are active immediately
        if not user.is_active:
            user.is_active = True
            user.save()
        return user
