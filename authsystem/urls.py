from django.urls import path
from .views import RegisterView, LoginView, LogoutView, GoogleLogin, AppleLogin, VerifyOTPView, AccountInactiveView, UserProfileUpdateView, UserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserView.as_view(), name='user'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('apple/', AppleLogin.as_view(), name='apple_login'),
    path('account-inactive/', AccountInactiveView.as_view(), name='account_inactive'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile_update'),
]
