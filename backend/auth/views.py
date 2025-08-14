
#? Views for the auth app
from rest_framework import status, generics, permissions                           #* DRF imports for API views and responses
from rest_framework.response import Response                                       #* DRF response class for API responses
from rest_framework.views import APIView                                           #* Base API view class
from rest_framework.authtoken.models import Token                                  #* Token model for authentication
from django.contrib.auth import login, logout                                      #* Django authentication functions
from django.core.mail import send_mail                                             #* Django email sending functionality
from django.conf import settings                                                   #* Django settings access
from django.template.loader import render_to_string                                #* Template rendering for emails
from django.utils.html import strip_tags                                           #* Strip HTML from templates
from .models import User, PasswordResetToken, EmailVerificationToken               #* Import custom models
from .serializers import (                                                         #* Import all serializers
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer
)


#? <|--------------User Registration View (Public Access)--------------|>
class UserRegistrationView(generics.CreateAPIView):
    """
    Public API endpoint for user registration
    URL: POST /api/auth/register/
    Purpose: Create new user accounts
    Features:
    - Creates user account
    - Generates authentication token
    - Sends email verification
    - Returns user data and token
    """
    
    queryset = User.objects.all()                                                  #* Queryset for the view
    serializer_class = UserRegistrationSerializer                                  #* Serializer for validation
    permission_classes = [permissions.AllowAny]                                    #* Allow public access (no authentication required)
    
    def create(self, request, *args, **kwargs):
        """
        Override create method to add custom logic
        Process: Validate data, create user, generate token, send verification email
        Returns: User data with authentication token
        """
        #* Validate registration data using serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)                                  #* Raise exception if validation fails
        
        #* Create new user account
        user = serializer.save()
        
        #* Create authentication token for immediate login
        token, created = Token.objects.get_or_create(user=user)
        
        #* Send email verification (non-blocking - continues if email fails)
        try:
            self.send_verification_email(user)
            email_sent = True
        except Exception as e:
            print(f"Failed to send verification email: {e}")                      #* Log error but don't fail registration
            email_sent = False
        
        #* Prepare response data
        user_data = UserProfileSerializer(user).data
        
        #* Return success response with user data and token
        return Response({
            'user': user_data,
            'token': token.key,
            'message': 'Cuenta creada exitosamente. Por favor, revisa tu email para el enlace de verificación.',
            'email_sent': email_sent
        }, status=status.HTTP_201_CREATED)
    
    def send_verification_email(self, user):
        """
        Send email verification to new user
        Process: Create verification token, compose email, send email
        Parameters: user - User instance to send verification to
        """
        #* Create email verification token
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        #* Email configuration
        subject = 'Verifica tu cuenta de AGAH Solutions'
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token.token}/"
        
        #* Email content
        message = f"""
        ¡Bienvenido a AGAH Solutions!
        
        Gracias por crear una cuenta con nosotros. Para completar tu registro y comenzar a realizar pedidos, por favor verifica tu dirección de email haciendo clic en el enlace a continuación:
        
        {verification_url}
        
        Este enlace de verificación expirará en 24 horas por razones de seguridad.
        
        Si no creaste esta cuenta, por favor ignora este email y la cuenta permanecerá sin verificar.
        
        ¿Preguntas? Contáctanos en {settings.CONTACT_EMAIL}
        
        Saludos cordiales,
        El equipo de AGAH Solutions
        """
        
        #* Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,                                                   #* Raise exception if email fails
        )


#? <|--------------User Login View (Public Access)--------------|>
class UserLoginView(APIView):
    """
    Public API endpoint for user login
    URL: POST /api/auth/login/
    Purpose: Authenticate existing users
    Features:
    - Validates credentials
    - Creates/retrieves authentication token
    - Updates last login timestamp
    - Returns user data and token
    """
    
    permission_classes = [permissions.AllowAny]                                    #* Allow public access
    
    def post(self, request):
        """
        Handle login POST request
        Process: Validate credentials, authenticate user, generate token
        Returns: User data with authentication token
        """
        #* Validate login credentials
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}                                           #* Pass request context for authentication
        )
        
        if serializer.is_valid():
            #* Get authenticated user from serializer
            user = serializer.validated_data['user']
            
            #* Log in user (updates last_login timestamp)
            login(request, user)
            
            #* Get or create authentication token
            token, created = Token.objects.get_or_create(user=user)
            
            #* Prepare user data for response
            user_data = UserProfileSerializer(user).data
            
            #* Return success response
            return Response({
                'user': user_data,
                'token': token.key,
                'message': 'Inicio de sesión exitoso'
            }, status=status.HTTP_200_OK)
        
        #* Return validation errors if login fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#? <|--------------User Logout View (Authenticated Users Only)--------------|>
class UserLogoutView(APIView):
    """
    Protected API endpoint for user logout
    URL: POST /api/auth/logout/
    Purpose: Securely log out authenticated users
    Features:
    - Deletes authentication token
    - Clears Django session
    - Invalidates client-side authentication
    """
    
    permission_classes = [permissions.IsAuthenticated]                             #* Require authentication
    
    def post(self, request):
        """
        Handle logout POST request
        Process: Delete token, logout user session
        Returns: Success confirmation
        """
        try:
            #* Delete user's authentication token (invalidates API access)
            request.user.auth_token.delete()
        except:
            #* Token might not exist, continue with logout
            pass
        
        #* Logout user from Django session
        logout(request)
        
        #* Return success response
        return Response({
            'message': 'Cierre de sesión exitoso. Has sido desconectado de forma segura.'
        }, status=status.HTTP_200_OK)


#? <|--------------User Profile View (Authenticated Users Only)--------------|>
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Protected API endpoint for user profile management
    URL: GET/PATCH /api/auth/profile/
    Purpose: View and update user profile information
    Features:
    - View current profile data
    - Update editable profile fields
    - Protects sensitive fields from modification
    """
    
    serializer_class = UserProfileSerializer                                       #* Serializer for profile data
    permission_classes = [permissions.IsAuthenticated]                             #* Require authentication
    
    def get_object(self):
        """
        Get the user object for profile operations
        Returns: Current authenticated user
        """
        return self.request.user


#? <|--------------Password Change View (Authenticated Users Only)--------------|>
class PasswordChangeView(APIView):
    """
    Protected API endpoint for password change
    URL: POST /api/auth/change-password/
    Purpose: Allow authenticated users to change their password
    Features:
    - Requires current password for security
    - Validates new password strength
    - Invalidates current token (forces re-login)
    """
    
    permission_classes = [permissions.IsAuthenticated]                             #* Require authentication
    
    def post(self, request):
        """
        Handle password change POST request
        Process: Validate passwords, update password, invalidate token
        Returns: Success confirmation
        """
        #* Validate password change data
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}                                           #* Pass request for current user access
        )
        
        if serializer.is_valid():
            #* Save new password
            user = serializer.save()
            
            #* Delete current authentication token for security
            #* This forces user to login again with new password
            try:
                request.user.auth_token.delete()
            except:
                pass
            
            #* Return success response
            return Response({
                            'message': 'Contraseña cambiada exitosamente. Por favor, inicia sesión nuevamente con tu nueva contraseña.'
                        }, status=status.HTTP_200_OK)
        
        #* Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#? <|--------------Password Reset Request View (Public Access)--------------|>
class PasswordResetRequestView(APIView):
    """
    Public API endpoint for password reset requests
    URL: POST /api/auth/password-reset/request/
    Purpose: Initiate password reset process via email
    Features:
    - Validates email
    - Creates reset token
    - Sends reset email
    - Secure (doesn't reveal if email exists)
    """
    
    permission_classes = [permissions.AllowAny]                                    #* Allow public access
    
    def post(self, request):
        """
        Handle password reset request
        Process: Validate email, create token, send email
        Returns: Generic success message (security)
        """
        #* Validate email address
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                #* Get user with this email
                user = User.objects.get(email=email, is_active=True)
                
                #* Create password reset token
                reset_token = PasswordResetToken.objects.create(user=user)
                
                #* Send password reset email
                self.send_reset_email(user, reset_token)
                
            except User.DoesNotExist:
                #* Don't reveal if email doesn't exist (security)
                pass
            
            #* Always return same response for security
            return Response({
                'message': 'Si tu dirección de email existe en nuestro sistema, recibirás un enlace para restablecer tu contraseña en breve.'
            }, status=status.HTTP_200_OK)
        
        #* Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_reset_email(self, user, reset_token):
        """
        Send password reset email to user
        Process: Compose email with reset link, send email
        Parameters: user - User instance, reset_token - PasswordResetToken instance
        """
        #* Email configuration
        subject = 'Restablece tu contraseña de AGAH Solutions'
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token.token}/"
        
        #* Email content
        message = f"""
        Hola {user.get_full_name()},
        
        Has solicitado restablecer la contraseña de tu cuenta de AGAH Solutions.
        
        Haz clic en el enlace a continuación para restablecer tu contraseña:
        {reset_url}
        
        Este enlace expirará en 1 hora por razones de seguridad.
        
        Si no solicitaste este restablecimiento de contraseña, por favor ignora este email y tu contraseña permanecerá sin cambios.
        
        Por seguridad, este enlace solo puede ser usado una vez.
        
        ¿Preguntas? Contáctanos en {settings.CONTACT_EMAIL}
        
        Saludos cordiales,
        El equipo de AGAH Solutions
        """
        
        #* Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


#? <|--------------Password Reset Confirm View (Public Access)--------------|>
class PasswordResetConfirmView(APIView):
    """
    Public API endpoint for password reset confirmation
    URL: POST /api/auth/password-reset/confirm/
    Purpose: Complete password reset with token from email
    Features:
    - Validates reset token
    - Updates password
    - Invalidates all user tokens
    - Marks reset token as used
    """
    
    permission_classes = [permissions.AllowAny]                                    #* Allow public access
    
    def post(self, request):
        """
        Handle password reset confirmation
        Process: Validate token and password, update password, cleanup tokens
        Returns: Success confirmation
        """
        #* Validate reset data
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            #* Reset password and mark token as used
            user = serializer.save()
            
            #* Delete all authentication tokens for this user
            #* This ensures security by invalidating all existing sessions
            Token.objects.filter(user=user).delete()
            
            #* Return success response
            return Response({
                'message': 'Contraseña restablecida exitosamente. Por favor, inicia sesión con tu nueva contraseña.'
            }, status=status.HTTP_200_OK)
        
        #* Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#? <|--------------Email Verification View (Public Access)--------------|>
class EmailVerificationView(APIView):
    """
    Public API endpoint for email verification
    URL: POST /api/auth/verify-email/
    Purpose: Verify user email address with token from email
    Features:
    - Validates verification token
    - Marks user as verified
    - Marks token as used
    """
    
    permission_classes = [permissions.AllowAny]                                    #* Allow public access
    
    def post(self, request):
        """
        Handle email verification
        Process: Validate token, mark user as verified, mark token as used
        Returns: Success confirmation
        """
        #* Validate verification token
        serializer = EmailVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            #* Verify email and mark token as used
            user = serializer.save()
            
            #* Return success response
            return Response({
                'message': '¡Email verificado exitosamente! Tu cuenta está ahora completamente activada y puedes realizar pedidos.'
            }, status=status.HTTP_200_OK)
        
        #* Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#? <|--------------Resend Verification Email View (Authenticated Users Only)--------------|>
class ResendVerificationEmailView(APIView):
    """
    Protected API endpoint to resend verification email
    URL: POST /api/auth/resend-verification/
    Purpose: Allow users to request new verification email
    Features:
    - Checks if user is already verified
    - Creates new verification token
    - Sends new verification email
    """
    
    permission_classes = [permissions.IsAuthenticated]                             #* Require authentication
    
    def post(self, request):
        """
        Handle resend verification email request
        Process: Check verification status, create token, send email
        Returns: Success or error message
        """
        user = request.user
        
        #* Check if user is already verified
        if user.is_verified:
            return Response({
                'message': 'Tu email ya está verificado. No es necesaria ninguna acción.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #* Create new verification token
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        #* Send verification email
        try:
            self.send_verification_email(user, verification_token)
            
            return Response({
                'message': 'Email de verificación enviado exitosamente. Por favor, revisa tu bandeja de entrada.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al enviar el email de verificación. Por favor, intenta nuevamente más tarde.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def send_verification_email(self, user, verification_token):
        """
        Send verification email to user
        Process: Compose email with verification link, send email
        Parameters: user - User instance, verification_token - EmailVerificationToken instance
        """
        #* Email configuration
        subject = 'Verifica tu cuenta de AGAH Solutions'
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token.token}/"
        
        #* Email content
        message = f"""
        Hola {user.get_full_name()},
        
        Por favor verifica tu dirección de email para completar la configuración de tu cuenta de AGAH Solutions.
        
        Haz clic en el enlace a continuación para verificar tu email:
        {verification_url}
        
        Este enlace de verificación expirará en 24 horas por razones de seguridad.
        
        Una vez verificado, podrás realizar pedidos y acceder a todas las funcionalidades.
        
        ¿Preguntas? Contáctanos en {settings.CONTACT_EMAIL}
        
        Saludos cordiales,
        El equipo de AGAH Solutions
        """
        
        #* Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


#? <|--------------Authentication Status Check View (Authenticated Users Only)--------------|>
class AuthStatusView(APIView):
    """
    Protected API endpoint to check authentication status
    URL: GET /api/auth/status/
    Purpose: Verify if user is authenticated and get current user data
    Features:
    - Validates current authentication
    - Returns current user information
    - Used by frontend to restore login state
    """
    
    permission_classes = [permissions.IsAuthenticated]                             #* Require authentication
    
    def get(self, request):
        """
        Get current authentication status and user data
        Process: Return authenticated user information
        Returns: Authentication status and user data
        """
        #* Get current user data
        user_data = UserProfileSerializer(request.user).data
        
        #* Return authentication confirmation with user data
        return Response({
            'authenticated': True,
            'user': user_data
        }, status=status.HTTP_200_OK)