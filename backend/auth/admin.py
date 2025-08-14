#? Admin configuration for the auth app
from django.contrib import admin                                                   #* Django admin interface
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin                  #* Base user admin for extension
from django.utils.html import format_html                                          #* HTML formatting for admin display
from django.utils import timezone                                                  #* Django timezone utilities
from .models import User, PasswordResetToken, EmailVerificationToken              #* Import custom models


#? <|--------------Custom User Admin Configuration--------------|>
@admin.register(User)                                                              #* Register User model with admin
class UserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for User model
    Purpose: Manage user accounts with enhanced features
    Features:
    - Visual status indicators for verification and activity
    - User type management with colors
    - Enhanced filtering and search capabilities
    - Mass actions for user management
    - Organized fieldsets for better user experience
    """
    
    #* Fields to display in the user list view
    list_display = [
        'email',                                                                   #* Primary identifier (email)
        'get_full_name',                                                           #* Full name display
        'user_type_display',                                                       #* User type with color coding
        'is_verified_display',                                                     #* Email verification status with icons
        'is_active',                                                               #* Account active status (raw field for editing)
        'created_at',                                                              #* Account creation date
        'last_login'                                                               #* Last login timestamp
    ]
    
    #* Filters that appear on the right side of the list view
    list_filter = [
        'user_type',                                                               #* Filter by user type (customer/admin/staff)
        'is_verified',                                                             #* Filter by email verification status
        'is_active',                                                               #* Filter by account activity status
        'is_staff',                                                                #* Filter by staff status
        'is_superuser',                                                            #* Filter by superuser status
        'created_at',                                                              #* Filter by creation date
        'last_login'                                                               #* Filter by last login date
    ]
    
    #* Fields that can be searched from the search box
    search_fields = [
        'email',                                                                   #* Search by email address
        'first_name',                                                              #* Search by first name
        'last_name',                                                               #* Search by last name
        'company'                                                                  #* Search by company name
    ]
    
    #* Fields that can be edited directly in the list view (without opening detail)
    list_editable = [
        'is_active'                                                                #* Quick toggle for account activation
    ]
    
    #* Organization of fields in the user detail form
    fieldsets = (
        ('Personal Information', {                                                 #* First section: Personal details
            'fields': ('email', 'first_name', 'last_name', 'phone', 'company')
        }),
        ('Account Settings', {                                                     #* Second section: Account configuration
            'fields': ('user_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser'),
            'classes': ('wide',)                                                   #* Make section wider for better layout
        }),
        ('Permissions', {                                                          #* Third section: Detailed permissions
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)                                               #* Collapsible section (advanced users only)
        }),
        ('Important Dates', {                                                      #* Fourth section: Timestamps
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)                                               #* Collapsible section
        }),
    )
    
    #* Special fieldset for adding new users (simpler form)
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),                                                  #* Wide layout for better UX
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'user_type'),
        }),
        ('Additional Information', {
            'classes': ('wide',),                                                  #* Additional optional fields
            'fields': ('phone', 'company'),
        }),
    )
    
    #* Read-only fields that cannot be edited
    readonly_fields = [
        'created_at',                                                              #* System-generated creation timestamp
        'updated_at',                                                              #* System-generated update timestamp
        'last_login'                                                               #* System-tracked last login
    ]
    
    #* Default ordering for the user list
    ordering = ['-created_at']                                                     #* Order by newest users first
    
    #* Override the username field configuration
    add_form_template = None                                                       #* Use default add form template
    
    def user_type_display(self, obj):
        """
        Custom display method for user type with color coding
        Purpose: Visual identification of user roles
        Returns: HTML with colored badge showing user type
        """
        colors = {
            'customer': '#28a745',                                                 #* Green for customers (most common)
            'admin': '#dc3545',                                                    #* Red for admins (high privilege)
            'staff': '#ffc107',                                                    #* Yellow for staff (medium privilege)
        }
        
        color = colors.get(obj.user_type, '#6c757d')                               #* Default gray for unknown types
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_user_type_display()
        )
    user_type_display.short_description = 'User Type'                             #* Column header name
    user_type_display.admin_order_field = 'user_type'                             #* Allow sorting by this field
    
    def is_verified_display(self, obj):
        """
        Custom display method for email verification status
        Purpose: Quick visual identification of verified accounts
        Returns: HTML with colored icon and text
        """
        if obj.is_verified:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Verified</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Not Verified</span>'
            )
    is_verified_display.short_description = 'Email Verified'                      #* Column header name
    is_verified_display.admin_order_field = 'is_verified'                         #* Allow sorting by this field
    
    def is_active_display(self, obj):
        """
        Custom display method for account active status
        Purpose: Quick visual identification of active/inactive accounts
        Returns: HTML with colored icon and text
        """
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Inactive</span>'
            )
    is_active_display.short_description = 'Account Status'                        #* Column header name
    is_active_display.admin_order_field = 'is_active'                             #* Allow sorting by this field
    
    #* Custom mass actions that appear in the dropdown above the list
    actions = ['verify_users', 'activate_users', 'deactivate_users', 'promote_to_staff']
    
    def verify_users(self, request, queryset):
        """
        Mass action to verify email for selected users
        Purpose: Manually verify users without email verification
        Use case: Customer service verifying users over phone
        """
        updated = queryset.update(is_verified=True)                                #* Update all selected users
        self.message_user(request, f'{updated} users marked as verified.')        #* Show success message
    verify_users.short_description = 'Mark selected users as verified'           #* Text shown in dropdown
    
    def activate_users(self, request, queryset):
        """
        Mass action to activate selected user accounts
        Purpose: Reactivate suspended accounts
        Use case: Reactivating accounts after review
        """
        updated = queryset.update(is_active=True)                                  #* Activate all selected users
        self.message_user(request, f'{updated} user accounts activated.')         #* Show success message
    activate_users.short_description = 'Activate selected user accounts'         #* Text shown in dropdown
    
    def deactivate_users(self, request, queryset):
        """
        Mass action to deactivate selected user accounts
        Purpose: Suspend problematic accounts without deletion
        Use case: Temporary account suspension
        """
        updated = queryset.update(is_active=False)                                 #* Deactivate all selected users
        self.message_user(request, f'{updated} user accounts deactivated.')       #* Show success message
    deactivate_users.short_description = 'Deactivate selected user accounts'     #* Text shown in dropdown
    
    def promote_to_staff(self, request, queryset):
        """
        Mass action to promote users to staff status
        Purpose: Grant admin access to trusted users
        Use case: Promoting customer service representatives
        """
        updated = queryset.update(user_type='staff', is_staff=True)                #* Promote to staff
        self.message_user(request, f'{updated} users promoted to staff status.')  #* Show success message
    promote_to_staff.short_description = 'Promote selected users to staff'       #* Text shown in dropdown


#? <|--------------Password Reset Token Admin--------------|>
@admin.register(PasswordResetToken)                                               #* Register PasswordResetToken model
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin configuration for PasswordResetToken model
    Purpose: Monitor and manage password reset tokens
    Features:
    - View all password reset requests
    - Monitor token usage and expiration
    - Security auditing capabilities
    - Cleanup of expired tokens
    """
    
    #* Fields to display in the token list view
    list_display = [
        'user',                                                                    #* User who requested reset
        'token_short',                                                             #* Shortened token for identification
        'created_at',                                                              #* When token was created
        'expires_at',                                                              #* When token expires
        'is_valid_display',                                                        #* Token validity status
        'is_used_display'                                                          #* Token usage status
    ]
    
    #* Filters for the right sidebar
    list_filter = [
        'is_used',                                                                 #* Filter by usage status
        'created_at',                                                              #* Filter by creation date
        'expires_at'                                                               #* Filter by expiration date
    ]
    
    #* Searchable fields
    search_fields = [
        'user__email',                                                             #* Search by user's email
        'user__first_name',                                                        #* Search by user's first name
        'user__last_name',                                                         #* Search by user's last name
        'token'                                                                    #* Search by token (for debugging)
    ]
    
    #* Read-only fields (tokens should not be manually edited)
    readonly_fields = [
        'user',                                                                    #* User cannot be changed
        'token',                                                                   #* Token cannot be modified
        'created_at',                                                              #* Creation time is immutable
        'expires_at',                                                              #* Expiration is calculated
        'is_used'                                                                  #* Usage status is system-controlled
    ]
    
    #* Default ordering
    ordering = ['-created_at']                                                     #* Show newest tokens first
    
    def has_add_permission(self, request):
        """
        Disable manual token creation
        Reason: Tokens should only be created programmatically for security
        Returns: False to prevent manual creation
        """
        return False                                                               #* Never allow manual token creation
    
    def token_short(self, obj):
        """
        Display shortened version of token for identification
        Purpose: Show enough of token to identify without revealing full token
        Returns: First 8 characters of token with ellipsis
        """
        return f"{str(obj.token)[:8]}..."
    token_short.short_description = 'Token'                                       #* Column header name
    
    def is_valid_display(self, obj):
        """
        Display token validity status with visual indicators
        Purpose: Quick identification of valid/invalid tokens
        Returns: HTML with colored status indicator
        """
        if obj.is_valid():
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Valid</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Invalid/Expired</span>'
            )
    is_valid_display.short_description = 'Valid'                                  #* Column header name
    
    def is_used_display(self, obj):
        """
        Display token usage status with visual indicators
        Purpose: Quick identification of used/unused tokens
        Returns: HTML with colored status indicator
        """
        if obj.is_used:
            return format_html(
                '<span style="color: orange; font-weight: bold;">✓ Used</span>'
            )
        else:
            return format_html(
                '<span style="color: blue; font-weight: bold;">✗ Not Used</span>'
            )
    is_used_display.short_description = 'Used'                                    #* Column header name


#? <|--------------Email Verification Token Admin--------------|>
@admin.register(EmailVerificationToken)                                           #* Register EmailVerificationToken model
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Admin configuration for EmailVerificationToken model
    Purpose: Monitor and manage email verification tokens
    Features:
    - View all email verification requests
    - Monitor token usage and expiration
    - Support customer service with verification issues
    - Security auditing capabilities
    """
    
    #* Fields to display in the token list view
    list_display = [
        'user',                                                                    #* User who needs verification
        'token_short',                                                             #* Shortened token for identification
        'created_at',                                                              #* When token was created
        'expires_at',                                                              #* When token expires
        'is_valid_display',                                                        #* Token validity status
        'is_used_display'                                                          #* Token usage status
    ]
    
    #* Filters for the right sidebar
    list_filter = [
        'is_used',                                                                 #* Filter by usage status
        'created_at',                                                              #* Filter by creation date
        'expires_at'                                                               #* Filter by expiration date
    ]
    
    #* Searchable fields
    search_fields = [
        'user__email',                                                             #* Search by user's email
        'user__first_name',                                                        #* Search by user's first name
        'user__last_name',                                                         #* Search by user's last name
        'token'                                                                    #* Search by token (for support)
    ]
    
    #* Read-only fields (tokens should not be manually edited)
    readonly_fields = [
        'user',                                                                    #* User cannot be changed
        'token',                                                                   #* Token cannot be modified
        'created_at',                                                              #* Creation time is immutable
        'expires_at',                                                              #* Expiration is calculated
        'is_used'                                                                  #* Usage status is system-controlled
    ]
    
    #* Default ordering
    ordering = ['-created_at']                                                     #* Show newest tokens first
    
    def has_add_permission(self, request):
        """
        Disable manual token creation
        Reason: Tokens should only be created programmatically for security
        Returns: False to prevent manual creation
        """
        return False                                                               #* Never allow manual token creation
    
    def token_short(self, obj):
        """
        Display shortened version of token for identification
        Purpose: Show enough of token to identify without revealing full token
        Returns: First 8 characters of token with ellipsis
        """
        return f"{str(obj.token)[:8]}..."
    token_short.short_description = 'Token'                                       #* Column header name
    
    def is_valid_display(self, obj):
        """
        Display token validity status with visual indicators
        Purpose: Quick identification of valid/invalid tokens
        Returns: HTML with colored status indicator
        """
        if obj.is_valid():
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Valid</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Invalid/Expired</span>'
            )
    is_valid_display.short_description = 'Valid'                                  #* Column header name
    
    def is_used_display(self, obj):
        """
        Display token usage status with visual indicators
        Purpose: Quick identification of used/unused tokens
        Returns: HTML with colored status indicator
        """
        if obj.is_used:
            return format_html(
                '<span style="color: orange; font-weight: bold;">✓ Used</span>'
            )
        else:
            return format_html(
                '<span style="color: blue; font-weight: bold;">✗ Not Used</span>'
            )
    is_used_display.short_description = 'Used'                                    #* Column header name