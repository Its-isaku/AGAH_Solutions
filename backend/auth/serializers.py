#? Serializers for the auth app
from rest_framework import serializers                                            #* Django REST Framework serializers for API data validation
from django.contrib.auth import authenticate                                      #* Django authentication system
from django.contrib.auth.password_validation import validate_password             #* Django password validation utilities
from django.core.exceptions import ValidationError                                #* Django validation error handling
from .models import User, PasswordResetToken, EmailVerificationToken              #* Import custom models from auth app


#? <|--------------User Registration Serializer--------------|>
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    Purpose: Handle new user account creation with validation
    Features:
    - Password confirmation validation
    - Django password strength validation
    - Username generation from email
    """
    
    #* Password fields with validation
    password = serializers.CharField(
        write_only=True,                                                           #* Don't return password in response
        min_length=8,                                                              #* Minimum password length
        help_text="Password must be at least 8 characters long"
    )
    
    password_confirm = serializers.CharField(
        write_only=True,                                                           #* Don't return in response
        help_text="Confirm your password by typing it again"
    )
    
    #* Meta configuration defining which model and fields to use
    class Meta:
        model = User                                                               #* Use custom User model
        fields = [
            'email',                                                               #* Primary identifier (replaces username)
            'first_name',                                                          #* Required for personalization
            'last_name',                                                           #* Required for full name
            'phone',                                                               #* Optional contact info
            'company',                                                             #* Optional for business customers
            'password',                                                            #* Account security
            'password_confirm'                                                     #* Password confirmation
        ]
        
        #* Extra validation rules for fields
        extra_kwargs = {
            'email': {'required': True},                                           #* Email is mandatory
            'first_name': {'required': True},                                      #* First name is mandatory
            'last_name': {'required': True},                                       #* Last name is mandatory
        }
    
    def validate_email(self, value):
        """
        Custom validation for email field
        Checks: Email uniqueness (case-insensitive)
        Returns: Normalized email (lowercase)
        """
        email_lower = value.lower()                                                #* Convert to lowercase for consistency
        if User.objects.filter(email=email_lower).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return email_lower
    
    def validate(self, data):
        """
        Cross-field validation (validates multiple fields together)
        Checks: Password confirmation match and strength
        Returns: Validated data dict
        """
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        #* Check if passwords match
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        
        #* Use Django's built-in password validation 
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)                                       #* Convert Django errors to DRF format
            })
        
        return data
    
    def create(self, validated_data):
        """
        Create new user instance
        Process: Remove password_confirm, set username to email, create user
        Returns: New User instance
        """
        #* Remove password confirmation from data
        validated_data.pop('password_confirm')
        
        #* Create user with validated data
        user = User.objects.create_user(
            username=validated_data['email'],                                      #* Set username to email for Django compatibility
            **validated_data                                                       #* Unpack all other validated data
        )
        
        return user


#? <|--------------User Login Serializer--------------|>
class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    Purpose: Validate login credentials and authenticate user
    Features:
    - Email-based authentication
    - Account status checking (active/inactive)
    - Security validation
    """
    
    #* Login credential fields
    email = serializers.EmailField(
        required=True,                                                             #* Email is mandatory for login
        help_text="Your registered email address"
    )
    
    password = serializers.CharField(
        required=True,                                                             #* Password is mandatory
        write_only=True,                                                           #* Don't return password in response
        help_text="Your account password"
    )
    
    def validate(self, data):
        """
        Validate login credentials
        Process: Extract credentials, attempt authentication, check account status
        Returns: Validated data with user object
        """
        email = data.get('email', '').lower()                                      #* Normalize email to lowercase
        password = data.get('password', '')
        
        if email and password:
            #* Attempt to authenticate user with Django's authentication system
            user = authenticate(
                request=self.context.get('request'),                              #* Pass request context for security
                username=email,                                                    #* Use email as username
                password=password
            )
            
            #* Check authentication result
            if not user:
                raise serializers.ValidationError(
                    'Invalid email or password. Please check your credentials and try again.'
                )
            
            #* Check if account is active
            if not user.is_active:
                raise serializers.ValidationError(
                    'Your account has been disabled. Please contact support for assistance.'
                )
            
            #* Add authenticated user to validated data
            data['user'] = user
            return data
        else:
            raise serializers.ValidationError(
                'Se requieren tanto el email como la contraseña para iniciar sesión.'
            )


#? <|--------------User Profile Serializer--------------|>
class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile display and updates
    Purpose: Handle user profile information (view and edit)
    Features:
    - Read-only computed fields
    - Restricted field editing
    - Safe profile updates
    """
    
    #* Computed read-only fields
    full_name = serializers.CharField(
        source='get_full_name',                                                    #* Use model method for full name
        read_only=True                                                             #* Cannot be directly set
    )
    
    #* Meta configuration for profile serialization
    class Meta:
        model = User
        fields = [
            'id',                                                                  #* User identifier
            'email',                                                               #* Email address
            'first_name',                                                          #* First name (editable)
            'last_name',                                                           #* Last name (editable)
            'full_name',                                                           #* Computed full name (read-only)
            'phone',                                                               #* Phone number (editable)
            'company',                                                             #* Company name (editable)
            'user_type',                                                           #* User type (read-only for security)
            'is_verified',                                                         #* Email verification status (read-only)
            'created_at',                                                          #* Account creation date (read-only)
            'last_login'                                                           #* Last login timestamp (read-only)
        ]
        
        #* Fields that cannot be edited by users (security and system fields)
        read_only_fields = [
            'id',                                                                  #* System-generated identifier
            'email',                                                               #* Email changes require separate process
            'user_type',                                                           #* Only admins can change user types
            'is_verified',                                                         #* Verification requires email process
            'created_at',                                                          #* Historical data
            'last_login'                                                           #* System-tracked data
        ]


#? <|--------------Password Change Serializer--------------|>
class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change by authenticated users
    Purpose: Allow users to change their password (requires current password)
    Features:
    - Current password verification
    - New password confirmation
    - Password strength validation
    """
    
    #* Password change fields
    current_password = serializers.CharField(
        required=True,                                                             #* Must provide current password for security
        write_only=True,                                                           #* Don't return in response
        help_text="Your current password for verification"
    )
    
    new_password = serializers.CharField(
        required=True,                                                             #* New password is required
        write_only=True,                                                           #* Don't return in response
        min_length=8,                                                              #* Minimum length requirement
        help_text="Your new password (minimum 8 characters)"
    )
    
    new_password_confirm = serializers.CharField(
        required=True,                                                             #* Confirmation required
        write_only=True,                                                           #* Don't return in response
        help_text="Confirm your new password"
    )
    
    def validate_current_password(self, value):
        """
        Validate current password
        Checks: Current password is correct for the authenticated user
        Returns: Validated current password
        """
        user = self.context['request'].user                                        #* Get authenticated user from request context
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value
    
    def validate(self, data):
        """
        Cross-field validation for password change
        Checks: New password confirmation and strength
        Returns: Validated data
        """
        new_password = data.get('new_password')
        new_password_confirm = data.get('new_password_confirm')
        
        #* Check if new passwords match
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las nuevas contraseñas no coinciden.'
            })
        
        #* Validate new password strength using Django's validators
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return data
    
    def save(self):
        """
        Save new password
        Process: Update user's password with new validated password
        Returns: Updated user instance
        """
        user = self.context['request'].user                                        #* Get authenticated user
        user.set_password(self.validated_data['new_password'])                     #* Set new password (hashed automatically)
        user.save()                                                                #* Save user to database
        return user


#? <|--------------Password Reset Request Serializer--------------|>
class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset requests
    Purpose: Handle password reset email requests
    Features:
    - Email validation
    - Security (doesn't reveal if email exists)
    """
    
    #* Email field for password reset
    email = serializers.EmailField(
        required=True,                                                             #* Email is required for reset
        help_text="Email address to send password reset link"
    )
    
    def validate_email(self, value):
        """
        Validate email for password reset
        Note: For security, we don't reveal whether email exists or not
        Returns: Normalized email
        """
        email_lower = value.lower()
        
        #* Check if user exists and is active
        try:
            user = User.objects.get(email=email_lower, is_active=True)
            return email_lower
        except User.DoesNotExist:
            #* For security, don't reveal if email exists
            #* Still return email to maintain consistent response time
            return email_lower


#? <|--------------Password Reset Confirm Serializer--------------|>
class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    Purpose: Handle password reset with token validation
    Features:
    - Token validation
    - New password confirmation
    - Password strength validation
    """
    
    #* Password reset confirmation fields
    token = serializers.UUIDField(
        required=True,                                                             #* Reset token from email
        help_text="Password reset token from email"
    )
    
    new_password = serializers.CharField(
        required=True,                                                             #* New password required
        write_only=True,                                                           #* Don't return in response
        min_length=8,                                                              #* Minimum length
        help_text="Your new password (minimum 8 characters)"
    )
    
    new_password_confirm = serializers.CharField(
        required=True,                                                             #* Confirmation required
        write_only=True,                                                           #* Don't return in response
        help_text="Confirm your new password"
    )
    
    def validate_token(self, value):
        """
        Validate password reset token
        Checks: Token exists and is still valid (not used, not expired)
        Returns: Validated token UUID
        """
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
            if not reset_token.is_valid():
                raise serializers.ValidationError(
                    'El token de restablecimiento de contraseña es inválido o ha expirado. Por favor solicita un nuevo enlace de restablecimiento.'
                )
            return value
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError(
                'Token de restablecimiento de contraseña inválido. Por favor solicita un nuevo enlace de restablecimiento.'
            )
    
    def validate(self, data):
        """
        Cross-field validation for password reset
        Checks: New password confirmation and strength
        Returns: Validated data
        """
        new_password = data.get('new_password')
        new_password_confirm = data.get('new_password_confirm')
        
        #* Check if passwords match
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las nuevas contraseñas no coinciden.'
            })
        
        #* Validate password strength
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return data
    
    def save(self):
        """
        Save new password and mark token as used
        Process: Get user from token, update password, mark token as used
        Returns: Updated user instance
        """
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']
        
        #* Get reset token and associated user
        reset_token = PasswordResetToken.objects.get(token=token)
        user = reset_token.user
        
        #* Update user's password
        user.set_password(new_password)                                            #* Hash and set new password
        user.save()                                                                #* Save user to database
        
        #* Mark token as used for security (one-time use)
        reset_token.mark_as_used()
        
        return user


#? <|--------------Email Verification Serializer--------------|>
class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification
    Purpose: Handle email verification token processing
    Features:
    - Token validation
    - Account activation
    """
    
    #* Email verification token field
    token = serializers.UUIDField(
        required=True,                                                             #* Verification token from email
        help_text="Email verification token from registration email"
    )
    
    def validate_token(self, value):
        """
        Validate email verification token
        Checks: Token exists and is still valid (not used, not expired)
        Returns: Validated token UUID
        """
        try:
            verification_token = EmailVerificationToken.objects.get(token=value)
            if not verification_token.is_valid():
                raise serializers.ValidationError(
                    'El token de verificación de email es inválido o ha expirado. Por favor solicita un nuevo email de verificación.'
                )
            return value
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError(
                'Token de verificación de email inválido. Por favor solicita un nuevo email de verificación.'
            )
    
    def save(self):
        """
        Verify user's email and mark token as used
        Process: Get user from token, mark as verified, mark token as used
        Returns: Updated user instance
        """
        token = self.validated_data['token']
        
        #* Get verification token and associated user
        verification_token = EmailVerificationToken.objects.get(token=token)
        user = verification_token.user
        
        #* Mark user as verified
        user.is_verified = True
        user.save()                                                                #* Save verification status
        
        #* Mark token as used for security (one-time use)
        verification_token.mark_as_used()
        
        return user