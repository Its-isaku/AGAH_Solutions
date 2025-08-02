
#? Nesesary imports
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import TypeService, CompanyConfiguration, Order, OrderItem
from .serializers import (
    TypeServiceSerializer, 
    CompanyConfigurationSerializer,
    OrderListSerializer, 
    OrderDetailSerializer, 
    OrderCreateSerializer,
    OrderItemSerializer,
    ContactFormSerializer,
    CartItemSerializer
)


#? <|------------------Homepage Data View------------------|>
class HomepageDataView(APIView):

    #* get method to retrieve homepage data 
    def get(self, request):
        
        #* Get featured services (first 3 active services)
        featured_services = TypeService.objects.filter(active=True)[:3]
        services_data = TypeServiceSerializer(featured_services, many=True).data
        
        #* Get basic company information
        company = CompanyConfiguration.objects.first()
        company_data = CompanyConfigurationSerializer(company).data if company else {}
        
        #* Get statistics for homepage
        recent_orders_count = Order.objects.filter(state='completed').count()
        
        #* Prepare response data
        response_data = {
            'featured_services': services_data,
            'company_info': {
                'name': company_data.get('company_name', 'AGAH Solutions'),
                'email': company_data.get('contact_email', ''),
                'phone': company_data.get('company_phone', ''),
            },
            'stats': {
                'completed_orders': recent_orders_count,
                'active_services': TypeService.objects.filter(active=True).count(),
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)



#? <|------------------Service Type Views------------------|>

#? class for listing all active service types 
class ServiceTypeListView(generics.ListAPIView):    
    
    #* queryset to filter active service types 
    queryset = TypeService.objects.filter(active=True)
    serializer_class = TypeServiceSerializer

#? class for retrieving details of a specific service type
class ServiceTypeDetailView(generics.RetrieveAPIView):

    #* queryset to filter active service types
    queryset = TypeService.objects.filter(active=True)
    serializer_class = TypeServiceSerializer
    lookup_field = 'type'



#? <|--------------Company Configuration View--------------|>
class CompanyConfigurationView(generics.RetrieveAPIView):

    #* serializer class for company configuration 
    serializer_class = CompanyConfigurationSerializer
    
    #* function to get the first company configuration object
    def get_object(self):
        return CompanyConfiguration.objects.first()



#? <|----------------------Order Views---------------------|>

#? class for listing all orders by customer email
class OrderListByCustomerView(generics.ListAPIView):

    #* serializer class for listing orders by customer email
    serializer_class = OrderListSerializer

    #* function to get the queryset for listing orders by customer email
    def get_queryset(self):
        customer_email = self.request.query_params.get('email', None)
        
        if customer_email:
            return Order.objects.filter(
                customer_email=customer_email
            ).order_by('-created_at')
        
        return Order.objects.none()


#? class for creating new orders 
class OrderCreateView(generics.CreateAPIView):

    #* queryset for all orders
    queryset = Order.objects.all()
    
    #* serializer class for creating orders
    serializer_class = OrderCreateSerializer
    
    #* function to create a new order and send confirmation email
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        #* Create the order
        order = serializer.save()
        
        #* Try to send confirmation email
        try:
            self.send_order_confirmation_email(order)
        except Exception as e:
            print(f"Failed to send confirmation email: {e}")
        
        #* Return detailed order information
        response_serializer = OrderDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def send_order_confirmation_email(self, order):
        config = CompanyConfiguration.objects.first()
        response_time = config.company_time_response_hours if config else 24
        
        subject = f"Confirmacion de Orden - {order.order_number}"
        message = f"""
        Estimado {order.customer_name},

        Gracias por su pedido! Hemos recibido su solicitud.

        Aquí están los detalles de su orden:
        ----------------------------------------
        Detalles:
        Número: {order.order_number}
        Precio Estimado: ${order.estimaded_price:.2f}
        Artículos: {order.items.count()}

        Revisaremos su pedido y le enviaremos una cotización detallada dentro de {response_time} horas.

        Puede rastrear el estado de su pedido utilizando el número de pedido anterior.

        Saludos cordiales, y que Dios le bendiga.
        AGAH Solutions Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=False,
        )

class OrderTrackingView(generics.RetrieveAPIView):
    
    #* queryset for all orders 
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer
    lookup_field = 'order_number'


#? <|-----------------Cart Management Views----------------|>
class AddItemToCartView(APIView):

    #* Post method to add an item to the cart 
    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        
        if serializer.is_valid():
            service_id = serializer.validated_data['service_id']
            
            try:
                service = TypeService.objects.get(id=service_id, active=True)
            except TypeService.DoesNotExist:
                return Response(
                    {'error': 'Service not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            #* Calculate estimated price temporarily
            quantity = serializer.validated_data['quantity']
            
            #* Create temporary OrderItem for calculations (don't save to DB)
            temp_item = OrderItem(
                service=service,
                quantity=quantity,
                length_dimensions=serializer.validated_data.get('length_dimensions'),
                width_dimensions=serializer.validated_data.get('width_dimensions'),
                height_dimensions=serializer.validated_data.get('height_dimensions'),
                needs_custom_design=serializer.validated_data.get('needs_custom_design', False),
                custom_design_price=serializer.validated_data.get('custom_design_price'),
            )
            
            #* Calculate price using model methods
            estimated_price = temp_item.calculate_service_price() * quantity
            
            #* Add design price if needed
            if temp_item.needs_custom_design and temp_item.custom_design_price:
                estimated_price += float(temp_item.custom_design_price)
            
            #* Prepare data for frontend
            cart_item_data = {
                'service_id': service.id,
                'service_name': service.name,
                'service_type': service.type,
                'description': serializer.validated_data['description'],
                'quantity': quantity,
                'length_dimensions': serializer.validated_data.get('length_dimensions'),
                'width_dimensions': serializer.validated_data.get('width_dimensions'),
                'height_dimensions': serializer.validated_data.get('height_dimensions'),
                'needs_custom_design': temp_item.needs_custom_design,
                'custom_design_price': temp_item.custom_design_price,
                'estimated_unit_price': temp_item.calculate_service_price(),
                'estimated_total_price': estimated_price
            }
            
            return Response({
                'success': True,
                'cart_item': cart_item_data,
                'message': 'Item added to cart successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CalculateCartTotalView(APIView):

    #* Post method to calculate cart total
    def post(self, request):
        cart_items = request.data.get('cart_items', [])
        
        total_estimated = 0
        total_items = 0
        
        #* Iterate through each cart item
        for item in cart_items:
            try:
                service = TypeService.objects.get(id=item['service_id'], active=True)
                quantity = item.get('quantity', 1)
                
                #* Create temporary item for calculations
                temp_item = OrderItem(
                    service=service,
                    quantity=quantity,
                    length_dimensions=item.get('length_dimensions'),
                    width_dimensions=item.get('width_dimensions'), 
                    height_dimensions=item.get('height_dimensions'),
                    needs_custom_design=item.get('needs_custom_design', False),
                    custom_design_price=item.get('custom_design_price'),
                )
                
                #* Calculate item price
                item_total = temp_item.calculate_service_price() * quantity
                
                #* Add custom design price if applicable
                if temp_item.needs_custom_design and temp_item.custom_design_price:
                    item_total += float(temp_item.custom_design_price)
                
                total_estimated += item_total
                total_items += quantity
                
            except (TypeService.DoesNotExist, KeyError, ValueError):
                continue
        
        return Response({
            'total_estimated_price': total_estimated,
            'total_items': total_items,
            'formatted_price': f"${total_estimated:,.2f} MXN",
            'breakdown': {
                'subtotal': total_estimated / 1.08,
                'tax': total_estimated - (total_estimated / 1.08),
                'total': total_estimated
            }
        }, status=status.HTTP_200_OK)

#? <|-------------------Contact Form View------------------|>
class ContactFormView(APIView):
    
    #* Post method to handle contact form submissions 
    def post(self, request):
        serializer = ContactFormSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            #* Prepare email content
            subject = f"Contact Form: {data['subject']}"
            message = f"""
                        Envío de formulario de contacto del sitio web:
                        
                        Nombre: {data['name']}
                        Correo: {data['email']}
                        Teléfono: {data.get('phone', 'No proporcionado')}
                        
                        Asunto: {data['subject']}
                        
                        Mensaje:
                        {data['message']}
                        
                        ---
                        Enviado desde el formulario de contacto del sitio web de AGAH Solutions
                        """
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                
                return Response(
                    {'message': 'Mensaje enviado exitosamente, te contactaremos pronto!.'}, 
                    status=status.HTTP_200_OK
                )
                
            except Exception as e:
                return Response(
                    {'error': 'Error al Mandar Correo, intentalo mas tarde.'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

