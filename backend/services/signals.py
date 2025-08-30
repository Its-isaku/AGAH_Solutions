
#? Django signals for automatic email notifications
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import Order

#? <|--------------Helper Functions for Emails--------------|>

def send_final_price_email(order):
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        html_message = render_to_string('emails/order_final_price.html', context)
        
        plain_message = f"""
            Hola {order.customer_name},
            
            ¡Tu precio final está listo para el Pedido #{order.order_number}!
            
            Precio Final: ${order.final_price} MXN
            
            Para confirmar tu pedido visita: {context['website_url']}/orders/confirm?order={order.order_number}
            
            Saludos,
            AGAH Solutions
        """
        
        send_mail(
            subject=f"¡Precio Final Listo! - Pedido #{order.order_number}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=True,
        )
        
        print(f"Final price email sent for order {order.order_number}")
        return True
        
    except Exception as e:
        print(f"Error sending final price email for order {order.order_number}: {e}")
        return False


def send_completion_email(order):
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
            'completion_date': timezone.now(),
            'total_days': (timezone.now() - order.created_at).days,
        }
        
        html_message = render_to_string('emails/order_completed.html', context)
        
        plain_message = f"""
            Hola {order.customer_name},
            
            ¡Excelentes noticias! Tu Pedido #{order.order_number} está completado.
            
            Tu proyecto ha sido terminado con la más alta calidad y está listo para recoger o enviar.
            
            Para coordinar la entrega, contáctanos:
            - Teléfono: +52 665 127 0811
            - Email: agahsolutions@gmail.com
            
            ¡Gracias por confiar en AGAH Solutions!
        """
        
        send_mail(
            subject=f"¡Tu Pedido Está Completado! - Pedido #{order.order_number}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=True,
        )
        
        print(f"Completion email sent for order {order.order_number}")
        return True
        
    except Exception as e:
        print(f"Error sending completion email for order {order.order_number}: {e}")
        return False


#? <|--------------Order Tracking Signals--------------|>

@receiver(pre_save, sender=Order)
def track_order_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_state = old_instance.state
            instance._old_final_price = old_instance.final_price
        except Order.DoesNotExist:
            instance._old_state = None
            instance._old_final_price = None
    else:
        instance._old_state = None
        instance._old_final_price = None


@receiver(post_save, sender=Order)
def handle_order_update(sender, instance, created, **kwargs):
    """Handle email notifications after order is saved"""
    
    if created:
        print(f"New order created: {instance.order_number}")
        return
    
    #* Get old values
    old_state = getattr(instance, '_old_state', None)
    old_final_price = getattr(instance, '_old_final_price', None)
    
    #* Send final price email when final_price is set for the first time
    if instance.final_price and not old_final_price:
        print(f"Sending final price email for order {instance.order_number}")
        send_final_price_email(instance)
    
    #* Send completion email when state changes to 'completed'
    elif instance.state == 'completed' and old_state != 'completed':
        print(f"Sending completion email for order {instance.order_number}")
        send_completion_email(instance)
    
    #* Log changes
    if old_state and old_state != instance.state:
        print(f"Order {instance.order_number} state changed: {old_state} -> {instance.state}")
    
    if old_final_price != instance.final_price:
        print(f"Order {instance.order_number} final price changed: {old_final_price} -> {instance.final_price}")