#? Views for the auth app
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
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
            
            #* Create user
            user = User.objects.create_user(
                username=email,  # Use email as username
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            #* Set user type if custom field exists
            if hasattr(user, 'user_type'):
                user.user_type = 'customer'
                user.save()
            
            #* Create token
            token, created = Token.objects.get_or_create(user=user)
            
            #* Login user
            login(request, user)
            
            #* Send welcome email
            try:
                self.send_welcome_email(user)
            except:
                pass  # Don't fail registration if email fails
            
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
        """Send welcome email to new user"""
        subject = "Welcome to AGAH Solutions"
        message = f"""
        Dear {user.first_name or 'Customer'},
        
        Welcome to AGAH Solutions! Your account has been created successfully.
        
        You can now:
        - Browse our services
        - Create orders
        - Track your order status
        - Contact our support team
        
        If you have any questions, please don't hesitate to contact us.
        
        Best regards,
        AGAH Solutions Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
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