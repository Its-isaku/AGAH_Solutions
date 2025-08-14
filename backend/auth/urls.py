
#? URLs for the auth app
from django.urls import path                                                       #* Django URL routing
from .views import (                                                               #* Import all authentication views
    #* Public Views (No Authentication Required)
    UserRegistrationView,
    UserLoginView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    EmailVerificationView,
    
    #* Protected Views (Authentication Required)
    UserLogoutView,
    UserProfileView,
    PasswordChangeView,
    ResendVerificationEmailView,
    AuthStatusView
)

#? <|--------------URL Patterns for Authentication App--------------|>
urlpatterns = [
    
    #? <|--------------Public Authentication Endpoints (No Auth Required)--------------|>
    #* User Registration
    path('api/auth/register/', UserRegistrationView.as_view(), name='user-register'),
    
    #* User Login
    path('api/auth/login/', UserLoginView.as_view(), name='user-login'),
    
    #* Password Reset request
    path('api/auth/password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    
    #* Password Reset confirm
    path('api/auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    #* Email Verification
    path('api/auth/verify-email/', EmailVerificationView.as_view(), name='email-verification'),
    
    
    #? <|--------------Protected Authentication Endpoints (Auth Required)--------------|>
    #* Session Logout
    path('api/auth/logout/', UserLogoutView.as_view(), name='user-logout'),

    #* Auth Status
    path('api/auth/status/', AuthStatusView.as_view(), name='auth-status'),
    
    #* User Profile Management
    path('api/auth/profile/', UserProfileView.as_view(), name='user-profile'),
    
    #* Password Management
    path('api/auth/change-password/', PasswordChangeView.as_view(), name='password-change'),
    
    #* Email Verification Management
    path('api/auth/resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
]