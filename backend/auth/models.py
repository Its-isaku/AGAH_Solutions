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
        extra_fields.setdefault('is_verified', True)  #* Superuser is auto-verified
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
    - Email verification system
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
    
    #* Account verification and status fields
    is_verified = models.BooleanField(
        default=False,                                                             #* New accounts start unverified
        help_text="Has the user verified their email address?"
    )
    
    #* Timestamp fields for tracking account lifecycle
    created_at = models.DateTimeField(
        auto_now_add=True,                                                         #* Automatically set when user is created
        help_text="When the user account was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,                                                             #* Automatically updated on each save
        help_text="When the user account was last updated"
    )
    
    #* Configure authentication to use email instead of username
    USERNAME_FIELD = 'email'                                                       #* Use email for login instead of username
    REQUIRED_FIELDS = ['first_name', 'last_name']                                  #* Required when creating superuser via command line
    
    #* Use custom manager
    objects = UserManager()                                                         #* Use our custom UserManager
    
    #* Meta configuration for the User model
    class Meta:
        verbose_name = "User"                                                      #* Singular name in admin
        verbose_name_plural = "Users"                                             #* Plural name in admin
        ordering = ['-created_at']                                                #* Order by newest first
    
    def __str__(self):
        """
        String representation of the user
        Returns: Full name and email for easy identification
        """
        return f"{self.first_name} {self.last_name} ({self.email})"               #* Display format in admin and queries
    
    def get_full_name(self):
        """
        Method to get user's full name
        Returns: First name + last name, handles empty names gracefully
        """
        return f"{self.first_name} {self.last_name}".strip()                      #* Strip removes extra spaces if names are empty
    
    def is_customer(self):
        """
        Check if user is a customer
        Returns: Boolean indicating if user type is customer
        """
        return self.user_type == 'customer'
    
    def is_admin_user(self):
        """
        Check if user has admin privileges
        Returns: Boolean indicating if user is admin or superuser
        """
        return self.user_type == 'admin' or self.is_superuser


#? <|--------------Password Reset Token Model--------------|>
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
        Returns: User email and partial token for identification
        """
        return f"Reset token for {self.user.email}"
    
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


#? <|--------------Email Verification Token Model--------------|>
class EmailVerificationToken(models.Model):
    """
    Model for handling email verification tokens
    Purpose: Verify user email addresses after registration
    Features:
    - Unique UUID tokens for security
    - Automatic expiration (24 hours)
    - One-time use tokens
    - User association for validation
    """
    
    #* Link to user requiring email verification
    user = models.ForeignKey(
        User,                                                                      #* Reference to custom User model
        on_delete=models.CASCADE,                                                  #* Delete tokens when user is deleted
        related_name='email_verification_tokens',                                  #* Reverse relation name
        help_text="User who needs email verification"
    )
    
    #* Unique token for email verification link
    token = models.UUIDField(
        default=uuid.uuid4,                                                        #* Generate random UUID
        unique=True,                                                               #* Ensure token uniqueness
        help_text="Unique token sent in verification email"
    )
    
    #* Timestamp when token was created
    created_at = models.DateTimeField(
        auto_now_add=True,                                                         #* Set automatically when token is created
        help_text="When the verification token was generated"
    )
    
    #* Timestamp when token expires
    expires_at = models.DateTimeField(
        help_text="When the token expires and becomes invalid"
    )
    
    #* Track if token has been used
    is_used = models.BooleanField(
        default=False,                                                             #* New tokens start as unused
        help_text="Has this token been used to verify email?"
    )
    
    #* Meta configuration for EmailVerificationToken model
    class Meta:
        verbose_name = "Email Verification Token"                                  #* Singular name in admin
        verbose_name_plural = "Email Verification Tokens"                         #* Plural name in admin
        ordering = ['-created_at']                                                #* Order by newest first
    
    def __str__(self):
        """
        String representation of the email verification token
        Returns: User email and purpose for identification
        """
        return f"Verification token for {self.user.email}"
    
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
        Logic: If expiration not set, set it to 24 hours from creation
        """
        if not self.expires_at:
            #* Set token to expire in 24 hours from creation (longer than password reset)
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)                                              #* Call parent save method