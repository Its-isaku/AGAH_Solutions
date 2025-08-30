#? Views for the services app
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .models import TypeService, Order, OrderItem, CompanyConfiguration
from .serializers import (
    TypeServiceSerializer,
    OrderSerializer,
    OrderItemSerializer,
    CompanyConfigurationSerializer,
    ContactFormSerializer
)


#? <|------------------Homepage View------------------|>
class HomepageView(APIView):

    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            print("Starting homepage view...")
            
            #* Get company configuration (opcional)
            company_config = None
            try:
                company_config = CompanyConfiguration.objects.first()
                print(f"Company config: {company_config is not None}")
            except Exception as e:
                print(f"No company config: {e}")
            
            #* Get featured services
            try:
                featured_services = TypeService.objects.filter(
                    active=True,
                    is_featured=True
                ).order_by('order_display')
                
                print(f"Found {featured_services.count()} featured services")
                for service in featured_services:
                    print(f"   - {service.name} (featured: {service.is_featured}, active: {service.active})")
                    
            except Exception as e:
                print(f"Error getting featured services: {e}")
                featured_services = TypeService.objects.none()  
            
            #* Calculate basic stats
            try:
                total_orders = Order.objects.count()
                completed_orders = Order.objects.filter(state='completed').count()  
                print(f"Orders - Total: {total_orders}, Completed: {completed_orders}")
            except Exception as e:
                print(f"Error calculating stats: {e}")
                total_orders = 0
                completed_orders = 0
            
            #* Serialize featured services
            try:
                featured_services_data = TypeServiceSerializer(featured_services, many=True).data
                print(f"Serialized {len(featured_services_data)} services")
            except Exception as e:
                print(f"Error serializing: {e}")
                featured_services_data = []
            
            #* Prepare homepage data
            homepage_data = {
                'company_name': company_config.company_name if company_config and hasattr(company_config, 'company_name') else 'AGAH Solutions',
                'hero_title': 'Welcome to',
                'hero_description': 'Cutting-Edge Solutions, Crafted to Perfection',
                'featured_services': featured_services_data,
                'company_stats': {
                    'total_projects': max(completed_orders, 50),
                    'happy_clients': max(completed_orders - 2, 45),
                    'years_experience': 5
                },
                'contact_info': {
                    'phone': '6651272495',
                    'email': 'Agahsolutions@gmail.com',
                    'address': 'Tecate, Baja California'
                }
            }
            
            print(f"Returning homepage data with {len(homepage_data['featured_services'])} featured services")
            
            return Response({
                'success': True,
                'data': homepage_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"CRITICAL ERROR: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            
            #* Fallback data - SIEMPRE devolver algo
            fallback_data = {
                'company_name': 'AGAH Solutions',
                'hero_title': 'Welcome to',
                'hero_description': 'Cutting-Edge Solutions, Crafted to Perfection',
                'featured_services': [],
                'company_stats': {
                    'total_projects': 50,
                    'happy_clients': 45,
                    'years_experience': 5
                },
                'contact_info': {
                    'phone': '6651272495',
                    'email': 'Agahsolutions@gmail.com',
                    'address': 'Tecate, BC'
                }
            }
            
            return Response({
                'success': True,
                'data': fallback_data,
                'message': 'Using fallback data'
            }, status=status.HTTP_200_OK)


#? <|--------------Public Views (No Authentication Required)--------------|>

class TypeServiceListView(APIView):
    """
    Public endpoint to list all active services
    MODIFICADO: Ahora retorna datos directos sin paginación y con success
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            #* Get all active services
            services = TypeService.objects.filter(active=True).order_by('order_display')
            serializer = TypeServiceSerializer(services, many=True)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'count': services.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TypeServiceDetailView(APIView):
    """
    Public endpoint to get details of a specific service
    MODIFICADO: Ahora retorna datos directos con success
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, pk):
        try:
            service = TypeService.objects.get(pk=pk, active=True)
            serializer = TypeServiceSerializer(service)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except TypeService.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Service not found',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompanyConfigurationView(APIView):
    """
    Public endpoint to get company information
    MODIFICADO: Ahora retorna datos directos sin paginación y con success
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            #* Get the first (and should be only) company configuration
            company = CompanyConfiguration.objects.first()
            
            if company:
                serializer = CompanyConfigurationSerializer(company)
                return Response({
                    'success': True,
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'No company configuration found',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactFormView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            #* Extract form data
            name = request.data.get('name', '').strip()
            email = request.data.get('email', '').strip()
            phone = request.data.get('phone', '').strip()
            subject = request.data.get('subject', '').strip()
            message = request.data.get('message', '').strip()
            
            #* Basic validation
            if not all([name, email, subject, message]):
                return Response({
                    'success': False,
                    'error': 'Todos los campos requeridos deben ser llenados'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #* Email validation
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            
            try:
                validate_email(email)
            except ValidationError:
                return Response({
                    'success': False,
                    'error': 'Email inválido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #* Send notification email to company
            try:
                self.send_company_notification({
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'subject': subject,
                    'message': message
                })
            except Exception as e:
                print(f"Error sending company notification: {e}")
                #* Don't fail the request if email fails
            
            return Response({
                'success': True,
                'message': 'Tu mensaje ha sido enviado exitosamente. Te responderemos pronto.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Contact form error: {e}")
            return Response({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def send_company_notification(self, contact_data):
        try:
            context = {
                'name': contact_data.get('name', ''),
                'email': contact_data.get('email', ''),
                'phone': contact_data.get('phone', ''),
                'subject': contact_data.get('subject', ''),
                'message': contact_data.get('message', ''),
                'submitted_at': timezone.now(),
                'company_time_response_hours': 24,  # Default from your config
            }
            
            #* Render HTML template
            html_message = render_to_string('emails/contact_form_company.html', context)
            
            #* Plain text version
            plain_message = f"""
                Nuevo mensaje de contacto recibido:

                Nombre: {context['name']}
                Email: {context['email']}
                Teléfono: {context['phone']}
                Asunto: {context['subject']}

                Mensaje:
                {context['message']}

                Fecha: {context['submitted_at'].strftime('%d/%m/%Y %H:%M')}
            """
            
            #* Send email
            send_mail(
                subject=f"Nuevo Contacto: {context['subject']}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],  #* Tu email de empresa
                html_message=html_message,
                fail_silently=True,
            )
            
            print(f"Company notification sent for contact from {context['email']}")
            return True
            
        except Exception as e:
            print(f"Error sending company notification: {e}")
            raise


class OrderTrackingView(APIView):
    """
    Public endpoint for order tracking by order number
    Allows tracking without login (for customer convenience)
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        order_number = request.data.get('order_number', '').strip()
        customer_email = request.data.get('customer_email', '').strip().lower()
        
        if not order_number or not customer_email:
            return Response({
                'success': False,
                'error': 'El número de pedido y el email del cliente son requeridos.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            #* Find order by number and email for security
            order = Order.objects.get(
                order_number=order_number,
                customer_email=customer_email
            )
            
            serializer = OrderSerializer(order)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Pedido no encontrado. Por favor, verifique su número de pedido y dirección de email.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)


#? <|--------------Protected Views (User Authentication Required)--------------|>

class OrderCreateView(APIView):
    """
    Protected endpoint to create a new order
    Requires: User authentication
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        #* Prepare order data with user info
        order_data = request.data.copy()
        order_data['user'] = request.user.id
        order_data['customer_name'] = request.user.get_full_name() or request.user.username
        order_data['customer_email'] = request.user.email
        
        serializer = OrderSerializer(data=order_data)
        
        if serializer.is_valid():
            order = serializer.save()
            
            #* Send confirmation email
            try:
                self.send_order_confirmation_email(order)
            except Exception as e:
                print(f"Failed to send confirmation email: {e}")
            
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Order created successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'error': 'Invalid order data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def send_order_confirmation_email(self, order):
        """Send order confirmation email to customer"""
        subject = f"Order Confirmation - {order.order_number}"
        message = f"""
        Estimado/a {order.customer_name},
        
        Gracias por su pedido. Hemos recibido su solicitud con el número de pedido: {order.order_number}
        
        Próximos pasos:
        1. Nuestro equipo revisará su pedido y archivos de diseño
        2. Le enviaremos una cotización detallada para su aprobación
        3. Una vez que apruebe la cotización, comenzaremos la producción
        
        Puede rastrear el estado de su pedido en cualquier momento usando su número de pedido.
        
        Si tiene alguna pregunta, no dude en contactarnos.
        
        Saludos cordiales,
        Equipo de AGAH Solutions
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=False,
        )


class UserOrdersListView(APIView):
    """
    Protected endpoint to list current user's orders
    MODIFICADO: Ahora retorna datos directos sin paginación y con success
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            #* Get all orders for the authenticated user
            orders = Order.objects.filter(user=request.user).order_by('-created_at')
            serializer = OrderSerializer(orders, many=True)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'count': orders.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserOrderDetailView(APIView):
    """
    Protected endpoint to get details of user's specific order
    MODIFICADO: Ahora retorna datos directos con success
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            #* Get order only if it belongs to the authenticated user
            order = Order.objects.get(pk=pk, user=request.user)
            serializer = OrderSerializer(order)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Order not found or you do not have permission to view it',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#? <|--------------Admin Views (Staff/Admin Only)--------------|>

class AdminOrderListView(APIView):
    """
    Admin endpoint to list all orders
    MODIFICADO: Ahora retorna datos directos sin paginación y con success
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        #* Check if user is staff or admin
        if not (request.user.is_staff or 
                request.user.user_type in ['admin', 'staff']):
            return Response({
                'success': False,
                'error': 'You do not have permission to access this resource',
                'data': []
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            #* Get all orders
            orders = Order.objects.all().order_by('-created_at')
            serializer = OrderSerializer(orders, many=True)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'count': orders.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminOrderDetailView(APIView):
    """
    Admin endpoint to view and update specific orders
    MODIFICADO: Ahora retorna datos directos con success
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        #* Check if user is staff or admin
        if not (request.user.is_staff or 
                request.user.user_type in ['admin', 'staff']):
            return Response({
                'success': False,
                'error': 'You do not have permission to access this resource',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            order = Order.objects.get(pk=pk)
            serializer = OrderSerializer(order)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Order not found',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, pk):
        #* Check if user is staff or admin
        if not (request.user.is_staff or 
                request.user.user_type in ['admin', 'staff']):
            return Response({
                'success': False,
                'error': 'You do not have permission to access this resource'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            order = Order.objects.get(pk=pk)
            serializer = OrderSerializer(order, data=request.data, partial=True)
            
            if serializer.is_valid():
                #* Track who updated the order
                serializer.save(assigned_user=request.user)
                
                #* Send status update email if state changed
                if 'state' in request.data:
                    try:
                        self.send_status_update_email(order)
                    except Exception as e:
                        print(f"Failed to send status update email: {e}")
                
                return Response({
                    'success': True,
                    'data': serializer.data,
                    'message': 'Order updated successfully'
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'error': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def send_status_update_email(self, order):
        """Send order status update email to customer"""
        status_messages = {
            'pending': 'Su pedido está siendo revisado por nuestro equipo.',
            'estimated': 'Hemos preparado una cotización para su pedido. Por favor, revise y confirme.',
            'confirmed': 'Su pedido ha sido confirmado y comenzará la producción pronto.',
            'in_progress': 'Su pedido está actualmente en producción.',
            'completed': 'Su pedido ha sido completado y está listo para retiro/entrega.',
            'canceled': 'Su pedido ha sido cancelado. Por favor, contáctenos para más información.'
        }
        
        subject = f"Order Update - {order.order_number}"
        status_message = status_messages.get(order.state, 'El estado de su pedido ha sido actualizado.')
        
        message = f"""
        Estimado/a {order.customer_name},
        
        Le informamos que el estado de su pedido {order.order_number} ha sido actualizado.
        
        Estado actual: {order.get_state_display()}
        {status_message}
        
        Puede rastrear su pedido en cualquier momento en nuestro sitio web.
        
        Si tiene alguna pregunta, no dude en contactarnos.
        
        Saludos cordiales,
        Equipo de AGAH Solutions
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=False,
        )