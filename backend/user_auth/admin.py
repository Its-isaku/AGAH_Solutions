#? Admin configuration for the auth app
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone

from .models import User, PasswordResetToken


#? <|--------------User Admin Configuration--------------|>
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for custom User model
    Purpose: Manage user accounts through Django admin interface
    Features:
    - Display key user information in list view
    - Filter and search capabilities
    - User type management
    - Account status overview
    """
    
    #* Fields to display in the user list view
    list_display = [
        'email',
        'get_full_name',
        'user_type',
        'is_active',
        'is_staff',
        'created_at',
        'last_login'
    ]
    
    #* Fields that can be clicked to view user detail
    list_display_links = ['email', 'get_full_name']
    
    #* Filters for the right sidebar
    list_filter = [
        'user_type',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at',
        'last_login'
    ]
    
    #* Fields that can be searched
    search_fields = [
        'email',
        'first_name',
        'last_name',
        'company'
    ]
    
    #* Default ordering (newest first)
    ordering = ['-created_at']
    
    #* Number of users per page
    list_per_page = 25
    
    #* Field organization for user detail/edit view
    fieldsets = (
        #* Basic Information Section
        (None, {
            'fields': ('email', 'password')
        }),
        
        #* Personal Information Section
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone', 'company')
        }),
        
        #* Account Type Section
        ('Account Type', {
            'fields': ('user_type',),
            'description': 'Determines user permissions and access level'
        }),
        
        #* Permissions Section
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        
        #* Important Dates Section
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    #* Fields for adding new users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'user_type', 'password1', 'password2'),
        }),
    )
    
    #* Readonly fields (cannot be edited)
    readonly_fields = ['created_at', 'updated_at', 'date_joined', 'last_login']
    
    #* Custom methods for list display
    def get_full_name(self, obj):
        """Display user's full name or email if no name provided"""
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'first_name'


#? <|--------------Password Reset Token Admin--------------|>
@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin configuration for PasswordResetToken model
    Purpose: Monitor and manage password reset requests
    Features:
    - View all password reset requests
    - Monitor token usage and expiration
    - Support customer service with password issues
    - Security auditing capabilities
    """
    
    #* Fields to display in the token list view
    list_display = [
        'user',
        'token_short',
        'created_at',
        'expires_at',
        'is_valid_display',
        'is_used_display'
    ]
    
    #* Filters for the right sidebar
    list_filter = [
        'is_used',
        'created_at',
        'expires_at'
    ]
    
    #* Fields that can be searched
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    
    #* Default ordering (newest first)
    ordering = ['-created_at']
    
    #* Readonly fields (security - cannot edit tokens)
    readonly_fields = ['user', 'token', 'created_at', 'expires_at', 'is_used']
    
    #* Number of tokens per page
    list_per_page = 50
    
    #* Custom methods for list display
    def token_short(self, obj):
        """Display shortened version of token for identification"""
        return f"{str(obj.token)[:8]}..."
    token_short.short_description = 'Token'
    
    def is_valid_display(self, obj):
        """Display token validity with color coding"""
        if obj.is_valid():
            return format_html('<span style="color: green;">✓ Valid</span>')
        else:
            return format_html('<span style="color: red;">✗ Invalid</span>')
    is_valid_display.short_description = 'Valid'
    
    def is_used_display(self, obj):
        """Display token usage status with color coding"""
        if obj.is_used:
            return format_html('<span style="color: orange;">✓ Used</span>')
        else:
            return format_html('<span style="color: blue;">○ Unused</span>')
    is_used_display.short_description = 'Used'