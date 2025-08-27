#? Models for the auth app
from django.db import models                                                       #* Django models import for database tables
from django.contrib.auth.models import AbstractUser, BaseUserManager             #* AbstractUser and BaseUserManager for custom user model
from django.utils import timezone                                                  #* Django timezone utilities for date/time handling
import uuid                                                                        #* UUID library for unique token generation


#? <|--------------Custom User Manager--------------|>
class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication
    Purpose: Handle user creation without username field
    Features:
    - Email-based user creation
    - Proper superuser creation
    - Validation and normalization
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with email and password
        """
        if not email:
            raise ValueError('Users must have an email address')
        
        #* Normalize email (lowercase domain)
        email = self.normalize_email(email)
        
        #* Set default values for required fields if not provided
        extra_fields.setdefault('first_name', '')
        extra_fields.setdefault('last_name', '')
        
        #* Create user instance
        user = self.model(
            email=email,
            username=email,  #* Set username to email for Django compatibility
            **extra_fields
        )
        
        #* Set password (hashed automatically)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with email and password
        """
        #* Set superuser defaults
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')
        
        #* Validate superuser fields
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


#? <|--------------Custom User Model (Extends Django's AbstractUser)--------------|>
class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser
    Purpose: Add additional fields specific to AGAH Solutions business needs
    Features:
    - Email-based authentication instead of username
    - Additional profile fields (phone, company)
    - User type classification (customer, admin, staff)
    - Account status tracking
    """
    
    #* Override email field to make it unique and required
    email = models.EmailField(
        unique=True,                                                               #* Email must be unique across all users
        help_text="User's email address (used for login instead of username)"
    )
    
    #* Additional profile fields
    phone = models.CharField(
        max_length=15,                                                             #* International phone number format
        blank=True,                                                                #* Optional field
        null=True,                                                                 #* Can be empty in database
        help_text="User's phone number (optional)"
    )
    
    #* Company field for business customers
    company = models.CharField(
        max_length=100,                                                            #* Company name length
        blank=True,                                                                #* Optional for individual customers
        null=True,                                                                 #* Can be empty in database
        help_text="Company name (optional, for business customers)"
    )
    
    #* User type classification system
    USER_TYPES = [
        ('customer', 'Customer'),                                                  #* Regular customers who place orders
        ('admin', 'Admin'),                                                        #* Full system administrators
        ('staff', 'Staff'),                                                        #* Staff members with limited admin access
    ]
    
    user_type = models.CharField(
        max_length=20,                                                             #* Length to accommodate user type values
        choices=USER_TYPES,                                                        #* Dropdown with predefined choices
        default='customer',                                                        #* New users are customers by default
        help_text="Type of user account (determines permissions)"
    )
    
    #* Timestamps for record keeping
    created_at = models.DateTimeField(
        auto_now_add=True,                                                         #* Set once when user is created
        help_text="When the user account was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,                                                             #* Update every time user is saved
        help_text="When the user account was last updated"
    )
    
    #* Set email as the unique identifier for authentication
    USERNAME_FIELD = 'email'                                                       #* Use email instead of username for login
    REQUIRED_FIELDS = []                                                           #* No additional required fields for superuser creation
    
    #* Link to custom user manager
    objects = UserManager()
    
    #* Meta configuration for User model
    class Meta:
        verbose_name = "User"                                                      #* Singular name in admin
        verbose_name_plural = "Users"                                             #* Plural name in admin
        ordering = ['-created_at']                                                #* Order by newest first
    
    def __str__(self):
        """
        String representation of the user
        Returns: User's email for identification
        """
        return self.email
    
    def get_full_name(self):
        """
        Get the user's full name
        Returns: First and last name combined, or email if no name provided
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.email
    
    def get_display_name(self):
        """
        Get display name for UI purposes
        Returns: First name if available, otherwise email
        """
        return self.first_name if self.first_name else self.email


#? <|--------------Password Reset Token Model (Keep this)--------------|>
class PasswordResetToken(models.Model):
    """
    Model for handling password reset tokens
    Purpose: Secure password reset functionality via email
    Features:
    - Unique UUID tokens for security
    - Automatic expiration (1 hour)
    - One-time use tokens
    - User association for validation
    """
    
    #* Link to user requesting password reset
    user = models.ForeignKey(
        User,                                                                      #* Reference to custom User model
        on_delete=models.CASCADE,                                                  #* Delete tokens when user is deleted
        related_name='password_reset_tokens',                                      #* Reverse relation name
        help_text="User who requested the password reset"
    )
    
    #* Unique token for password reset link
    token = models.UUIDField(
        default=uuid.uuid4,                                                        #* Generate random UUID
        unique=True,                                                               #* Ensure token uniqueness across all tokens
        help_text="Unique token sent in password reset email"
    )
    
    #* Timestamp when token was created
    created_at = models.DateTimeField(
        auto_now_add=True,                                                         #* Set automatically when token is created
        help_text="When the password reset token was generated"
    )
    
    #* Timestamp when token expires
    expires_at = models.DateTimeField(
        help_text="When the token expires and becomes invalid"
    )
    
    #* Track if token has been used
    is_used = models.BooleanField(
        default=False,                                                             #* New tokens start as unused
        help_text="Has this token been used to reset password?"
    )
    
    #* Meta configuration for PasswordResetToken model
    class Meta:
        verbose_name = "Password Reset Token"                                      #* Singular name in admin
        verbose_name_plural = "Password Reset Tokens"                             #* Plural name in admin
        ordering = ['-created_at']                                                #* Order by newest first
    
    def __str__(self):
        """
        String representation of the password reset token
        Returns: User email and purpose for identification
        """
        return f"Password reset token for {self.user.email}"
    
    def is_valid(self):
        """
        Check if token is still valid for use
        Returns: Boolean indicating if token can be used
        Conditions: Not used AND not expired
        """
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """
        Mark token as used (one-time use security)
        Action: Sets is_used to True and saves to database
        """
        self.is_used = True
        self.save()
    
    def save(self, *args, **kwargs):
        """
        Override save method to automatically set expiration time
        Logic: If expiration not set, set it to 1 hour from creation
        """
        if not self.expires_at:
            #* Set token to expire in 1 hour from creation
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)                                              #* Call parent save method