#? Signal handlers for order state changes and email notifications
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Order

#? <|--------------Email Signal Handlers--------------|>

@receiver(pre_save, sender=Order)
def track_order_state_changes(sender, instance, **kwargs):
    """
    Track when order state changes to send appropriate emails
    """
    if instance.pk:  #* Only for existing orders
        try:
            old_order = Order.objects.get(pk=instance.pk)
            
            #* Check if state changed
            if old_order.state != instance.state:
                instance._state_changed = True
                instance._old_state = old_order.state
            else:
                instance._state_changed = False
                
            #* Check if final price was just set
            if not old_order.final_price and instance.final_price:
                instance._final_price_set = True
            else:
                instance._final_price_set = False
                
        except Order.DoesNotExist:
            instance._state_changed = False
            instance._final_price_set = False

@receiver(post_save, sender=Order)
def send_order_emails(sender, instance, created, **kwargs):
    """
    Send emails based on order state changes using new templates
    """
    
    #* Send confirmation email for new orders
    if created:
        send_order_confirmation_email(instance)
        return
    
    #* Check for state changes
    elif hasattr(instance, '_state_changed') and instance._state_changed:
        
        #* Send estimate email when state changes to estimated (only if no final price)
        if instance.state == 'estimated' and instance.estimaded_price and not instance.final_price:
            send_estimate_email(instance)
        
        #* Send final price email when final_price exists
        elif instance.state == 'estimated' and instance.final_price:
            send_final_price_email(instance)
        
        #* Send confirmation email when customer confirms
        elif instance.state == 'confirmed':
            send_confirmed_email(instance)
        
        #* Send in progress email
        elif instance.state == 'in_progress':
            send_in_progress_email(instance)
        
        #* Send completion email
        elif instance.state == 'completed':
            send_completion_email(instance)
            
        #* Send cancellation email
        elif instance.state == 'canceled':
            send_cancellation_email(instance)

#? <|--------------Email Helper Functions--------------|>

def send_order_confirmation_email(order):
    """Send initial order confirmation email when order is created"""
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'order_items': order.items.all(),
            'contact_email': getattr(settings, 'CONTACT_EMAIL', 'agahsolutions@gmail.com'),
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        # Use the welcome email template for new orders
        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"¡Pedido Recibido! - {order.order_number} | AGAH Solutions",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"Welcome/confirmation email sent for order {order.order_number}")
        return True
        
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False

def send_estimate_email(order):
    """Send estimate/quote email - ONLY when there's no final price yet"""
    try:
        if order.final_price:
            print(f"Skipping estimate email for order {order.order_number} - final price already exists")
            return False
            
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'order_items': order.items.all(),
            'estimated_price': order.estimaded_price,
            'contact_email': getattr(settings, 'CONTACT_EMAIL', 'agahsolutions@gmail.com'),
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        html_message = render_to_string('emails/order_estimate.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"Cotización Lista - {order.order_number} | AGAH Solutions",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"Estimate email sent for order {order.order_number}")
        return True
        
    except Exception as e:
        print(f"Error sending estimate email: {e}")
        return False

def send_final_price_email(order):
    """Send email with final price when pricing is finalized"""
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'order_items': order.items.all(),
            'final_price': order.final_price,
            'delivery_time_days': order.estimated_completion_date_days,
            'contact_email': getattr(settings, 'CONTACT_EMAIL', 'agahsolutions@gmail.com'),
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        html_message = render_to_string('emails/order_final_price.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"Precio Final - {order.order_number} | AGAH Solutions",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"Final price email sent for order {order.order_number}")
        return True
        
    except Exception as e:
        print(f"Error sending final price email: {e}")
        return False

def send_confirmed_email(order):
    """Send email when customer confirms the order"""
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'final_price': order.final_price or order.estimaded_price,
            'delivery_time_days': order.estimated_completion_date_days,
            'order_items': order.items.all(),
            'contact_email': getattr(settings, 'CONTACT_EMAIL', 'agahsolutions@gmail.com'),
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        html_message = render_to_string('emails/order_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"¡Pedido Confirmado! - {order.order_number} | AGAH Solutions",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"Order confirmed email sent for order {order.order_number}")
        return True
        
    except Exception as e:
        print(f"Error sending confirmed email: {e}")
        return False

def send_in_progress_email(order):
    """Send email when order starts production"""
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'order_items': order.items.all(),
            'delivery_time_days': order.estimated_completion_date_days,
            'contact_email': getattr(settings, 'CONTACT_EMAIL', 'agahsolutions@gmail.com'),
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        html_message = render_to_string('emails/order_in_progres.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"En Producción - {order.order_number} | AGAH Solutions",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"In progress email sent for order {order.order_number}")
        return True
        
    except Exception as e:
        print(f"Error sending in progress email: {e}")
        return False

def send_completion_email(order):
    """Send email when order is completed"""
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'order_items': order.items.all(),
            'contact_email': getattr(settings, 'CONTACT_EMAIL', 'agahsolutions@gmail.com'),
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        html_message = render_to_string('emails/order_completed.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"¡Pedido Completado! - {order.order_number} | AGAH Solutions",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"Completion email sent for order {order.order_number}")
        return True
        
    except Exception as e:
        print(f"Error sending completion email: {e}")
        return False

def send_cancellation_email(order):
    """Send email when order is cancelled"""
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'order_items': order.items.all(),
            'contact_email': getattr(settings, 'CONTACT_EMAIL', 'agahsolutions@gmail.com'),
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        html_message = render_to_string('emails/order_canceld.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"Pedido Cancelado - {order.order_number} | AGAH Solutions",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"Cancellation email sent for order {order.order_number}")
        return True
        
    except Exception as e:
        print(f"Error sending cancellation email: {e}")
        return False