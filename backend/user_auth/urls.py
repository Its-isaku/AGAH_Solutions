#? URLs for the auth app
from django.urls import path                                                       
from .views import (                                                               
    #* Import only the views that actually exist in views.py
    LoginView,
    SignupView,
    LogoutView,
    ProfileView,
    VerifyTokenView,
    ChangePasswordView,
)

#? <|--------------URL Patterns for Authentication App--------------|>
urlpatterns = [
    
    #? <|--------------Public Authentication Endpoints (No Auth Required)--------------|>
    #* User Registration - matches your SignupView
    path('api/auth/register/', SignupView.as_view(), name='user-register'),
    
    #* User Login - matches your LoginView  
    path('api/auth/login/', LoginView.as_view(), name='user-login'),
    
    
    #? <|--------------Protected Authentication Endpoints (Auth Required)--------------|>
    #* Session Logout - matches your LogoutView
    path('api/auth/logout/', LogoutView.as_view(), name='user-logout'),

    #* Auth Status - matches your VerifyTokenView
    path('api/auth/status/', VerifyTokenView.as_view(), name='auth-status'),
    
    #* User Profile Management - matches your ProfileView
    path('api/auth/profile/', ProfileView.as_view(), name='user-profile'),
    
    #* Password Management - matches your ChangePasswordView
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='password-change'),
]