#? Views for the auth app
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


User = get_user_model()


class LoginView(APIView):

    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        
        if not email or not password:
            return Response({
                'success': False,
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            #* Authenticate user
            user = authenticate(request, username=email, password=password)
            
            if user:
                #* Create or get token
                token, created = Token.objects.get_or_create(user=user)
                
                #* Login user
                login(request, user)
                
                return Response({
                    'success': True,
                    'data': {
                        'token': token.key,
                        'user': {
                            'id': user.id,
                            'email': user.email,
                            'username': user.username,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'user_type': getattr(user, 'user_type', 'customer')
                        }
                    },
                    'message': 'Login successful'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignupView(APIView):
    """
    User registration endpoint
    Creates new user and returns token with success flag
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            #* Extract data
            email = request.data.get('email', '').strip().lower()
            password = request.data.get('password', '')
            confirm_password = request.data.get('confirm_password', '')
            first_name = request.data.get('first_name', '').strip()
            last_name = request.data.get('last_name', '').strip()
            
            #* Validate required fields
            if not email or not password:
                return Response({
                    'success': False,
                    'error': 'Email and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #* Check passwords match
            if password != confirm_password:
                return Response({
                    'success': False,
                    'error': 'Passwords do not match'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #* Check if user exists
            if User.objects.filter(email=email).exists():
                return Response({
                    'success': False,
                    'error': 'User with this email already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #* Create user - No email verification needed
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='customer'
            )
            
            #* Create token
            token, created = Token.objects.get_or_create(user=user)
            
            #* Login user
            login(request, user)
            
            #* Send beautiful welcome email
            try:
                self.send_welcome_email(user)
            except Exception as e:
                print(f"Welcome email failed: {e}")  # Log error but don't fail registration
            
            return Response({
                'success': True,
                'data': {
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'user_type': getattr(user, 'user_type', 'customer')
                    }
                },
                'message': 'Account created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def send_welcome_email(self, user):
        """Send beautiful welcome email using HTML template"""
        subject = "¡Bienvenido a AGAH Solutions!"
        
        # Context for the template
        context = {
            'user_name': user.get_display_name(),
            'website_url': 'http://localhost:3000',  # Update with your actual domain
            'user': user
        }
        
        # Render HTML template
        html_message = render_to_string('emails/welcome_email.html', context)
        
        # Create plain text version
        plain_message = f"""
        Hola {user.get_display_name()},
        
        ¡Bienvenido a AGAH Solutions! Tu cuenta ha sido creada exitosamente.
        
        Ahora puedes:
        - Explorar nuestro catálogo completo de servicios
        - Crear y gestionar tus pedidos personalizados  
        - Hacer seguimiento del estado de tus proyectos
        - Contactar con nuestro equipo de soporte especializado
        - Acceder a cotizaciones detalladas y estimados
        
        Si tienes alguna pregunta, no dudes en contactarnos.
        
        Saludos,
        El equipo de AGAH Solutions
        
        AGAH Solutions
        Email: agahsolutions@gmail.com
        Teléfono: +52 665 127 0811
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,  # This sends the beautiful HTML version
            fail_silently=True,
        )


class LogoutView(APIView):
    """
    User logout endpoint
    Deletes token and logs out user with success flag
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            #* Delete token
            Token.objects.filter(user=request.user).delete()
            
            #* Logout user
            logout(request)
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(APIView):
    """
    User profile endpoint
    Get and update user profile with success flag
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            
            return Response({
                'success': True,
                'data': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'date_joined': user.date_joined,
                    'user_type': getattr(user, 'user_type', 'customer')
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        try:
            user = request.user
            
            #* Update allowed fields
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            
            user.save()
            
            return Response({
                'success': True,
                'data': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': getattr(user, 'user_type', 'customer')
                },
                'message': 'Profile updated successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyTokenView(APIView):
    """
    Verify if token is valid
    Returns user data if valid with success flag
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            
            return Response({
                'success': True,
                'valid': True,
                'data': {
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'user_type': getattr(user, 'user_type', 'customer')
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'valid': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    """
    Change password endpoint
    Requires old password and new password with success flag
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            old_password = request.data.get('old_password', '')
            new_password = request.data.get('new_password', '')
            confirm_password = request.data.get('confirm_password', '')
            
            #* Validate fields
            if not old_password or not new_password:
                return Response({
                    'success': False,
                    'error': 'Old password and new password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #* Check old password
            if not user.check_password(old_password):
                return Response({
                    'success': False,
                    'error': 'Current password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #* Check passwords match
            if new_password != confirm_password:
                return Response({
                    'success': False,
                    'error': 'New passwords do not match'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #* Change password
            user.set_password(new_password)
            user.save()
            
            #* Create new token
            Token.objects.filter(user=user).delete()
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'success': True,
                'data': {
                    'token': token.key
                },
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)