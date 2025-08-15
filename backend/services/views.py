#? Views for the services app
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
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
    """
    Returns homepage data combining services, company info and stats
    """
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
            
            #* Calculate basic stats (CORRECCIÓN AQUÍ: usar 'state' no 'status')
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
            
            return Response(homepage_data, status=status.HTTP_200_OK)
            
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
            
            return Response(fallback_data, status=status.HTTP_200_OK)
            


#? <|--------------Public Views (No Authentication Required)--------------|>

class TypeServiceListView(generics.ListAPIView):
    """
    Public endpoint to list all active services
    Used by: Homepage, Services page
    """
    queryset = TypeService.objects.filter(active=True)
    serializer_class = TypeServiceSerializer
    permission_classes = [permissions.AllowAny]  #* Public access


class TypeServiceDetailView(generics.RetrieveAPIView):
    """
    Public endpoint to get details of a specific service
    Used by: Service detail modals, order forms
    """
    queryset = TypeService.objects.filter(active=True)
    serializer_class = TypeServiceSerializer
    permission_classes = [permissions.AllowAny]  #* Public access


class CompanyConfigurationView(generics.ListAPIView):
    """
    Public endpoint to get company information
    Used by: About page, Contact page, Footer
    """
    queryset = CompanyConfiguration.objects.all()
    serializer_class = CompanyConfigurationSerializer
    permission_classes = [permissions.AllowAny]  #* Public access


class ContactFormView(APIView):
    """
    Public endpoint for contact form submissions
    Used by: Contact page
    """
    permission_classes = [permissions.AllowAny]  #* Public access
    
    def post(self, request):
        serializer = ContactFormSerializer(data=request.data)
        
        if serializer.is_valid():
            #* Send email to company
            try:
                subject = f"Contact Form: {serializer.validated_data['subject']}"
                message = f"""
                Nueva consulta desde el formulario de contacto:
                
                Nombre: {serializer.validated_data['name']}
                Email: {serializer.validated_data['email']}
                Teléfono: {serializer.validated_data.get('phone', 'No proporcionado')}
                Asunto: {serializer.validated_data['subject']}
                
                Mensaje:
                {serializer.validated_data['message']}
                
                Enviado desde el formulario de contacto del sitio web de AGAH Solutions.
                """
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                
                return Response({
                    'message': 'Su mensaje ha sido enviado exitosamente. Nos pondremos en contacto con usted pronto.'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': 'Error al enviar el mensaje. Por favor, inténtelo de nuevo más tarde.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#? <|--------------Protected Views (Authentication Required)--------------|>

class OrderCreateView(generics.CreateAPIView):
    """
    Protected endpoint to create new orders
    Requires: User authentication
    Used by: Checkout process
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]  #* REQUIRES LOGIN
    
    def perform_create(self, serializer):
        #* Automatically assign the authenticated user and their data
        serializer.save(
            user=self.request.user,
            customer_name=self.request.user.get_full_name(),
            customer_email=self.request.user.email
        )
    
    def create(self, request, *args, **kwargs):
        #* Custom create to send confirmation email
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            order = Order.objects.get(id=response.data['id'])
            
            #* Send order confirmation email
            try:
                self.send_order_confirmation_email(order)
            except Exception as e:
                print(f"Failed to send order confirmation email: {e}")
        
        return response
    
    def send_order_confirmation_email(self, order):
        """Send order confirmation email to customer"""
        subject = f"Order Confirmation - {order.order_number}"
        
        #* Build order items list
        items_list = ""
        for item in order.items.all():
            items_list += f"- {item.service.name} x{item.quantity}\n"
        
        message = f"""
        Hola {order.customer_name},
        
        ¡Gracias por su pedido! Hemos recibido su solicitud y la procesaremos en breve.
        
        Detalles del Pedido:
        Número de Pedido: {order.order_number}
        Fecha del Pedido: {order.created_at.strftime('%d de %B de %Y a las %I:%M %p')}
        
        Servicios Solicitados:
        {items_list}
        
        Próximos Pasos:
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


class UserOrdersListView(generics.ListAPIView):
    """
    Protected endpoint to list current user's orders
    Requires: User authentication
    Used by: My Orders page, Order history
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]  #* REQUIRES LOGIN
    
    def get_queryset(self):
        #* Only return orders for the authenticated user
        return Order.objects.filter(user=self.request.user)


class UserOrderDetailView(generics.RetrieveAPIView):
    """
    Protected endpoint to get details of user's specific order
    Requires: User authentication + ownership
    Used by: Order detail page, Order tracking
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]  #* REQUIRES LOGIN
    
    def get_queryset(self):
        #* Only return orders for the authenticated user
        return Order.objects.filter(user=self.request.user)


class OrderTrackingView(APIView):
    """
    Public endpoint for order tracking by order number
    Allows tracking without login (for customer convenience)
    Used by: Order tracking page
    """
    permission_classes = [permissions.AllowAny]  #* Public access
    
    def post(self, request):
        order_number = request.data.get('order_number', '').strip()
        customer_email = request.data.get('customer_email', '').strip().lower()
        
        if not order_number or not customer_email:
            return Response({
                'error': 'El número de pedido y el email del cliente son requeridos.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            #* Find order by number and email for security
            order = Order.objects.get(
                order_number=order_number,
                customer_email=customer_email
            )
            
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response({
                'error': 'Pedido no encontrado. Por favor, verifique su número de pedido y dirección de email.'
            }, status=status.HTTP_404_NOT_FOUND)


#? <|--------------Admin Views (Staff/Admin Only)--------------|>

class AdminOrderListView(generics.ListAPIView):
    """
    Admin endpoint to list all orders
    Requires: Staff or admin permissions
    Used by: Admin dashboard, Order management
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]  #* REQUIRES LOGIN
    
    def get_queryset(self):
        #* Only allow staff and admin users
        if not (self.request.user.is_staff or 
                self.request.user.user_type in ['admin', 'staff']):
            return Order.objects.none()  #* Return empty queryset
        
        return Order.objects.all()


class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    """
    Admin endpoint to view and update specific orders
    Requires: Staff or admin permissions
    Used by: Admin order management, Status updates
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]  #* REQUIRES LOGIN
    
    def get_queryset(self):
        #* Only allow staff and admin users
        if not (self.request.user.is_staff or 
                self.request.user.user_type in ['admin', 'staff']):
            return Order.objects.none()  #* Return empty queryset
        
        return Order.objects.all()
    
    def perform_update(self, serializer):
        #* Track who updated the order
        serializer.save(assigned_user=self.request.user)
        
        #* Send status update email if state changed
        if 'state' in serializer.validated_data:
            order = serializer.instance
            try:
                self.send_status_update_email(order)
            except Exception as e:
                print(f"Failed to send status update email: {e}")
    
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
        Hola {order.customer_name},
        
        El estado de su pedido ha sido actualizado:
        
        Número de Pedido: {order.order_number}
        Estado Actual: {order.get_state_display()}
        
        {status_message}
        
        Puede rastrear su pedido en cualquier momento usando su número de pedido en nuestro sitio web.
        
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