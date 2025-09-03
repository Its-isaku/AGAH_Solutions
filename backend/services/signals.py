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
    Send emails based on order state changes
    """
    
    #* Send confirmation email for new orders
    if created:
        send_order_confirmation_email(instance)
    
    #* Check for state changes
    elif hasattr(instance, '_state_changed') and instance._state_changed:
        
        #* Send estimate email
        if instance.state == 'estimated' and instance.estimaded_price:
            send_estimate_email(instance)
        
        #* Send confirmation email when customer confirms
        elif instance.state == 'confirmed':
            send_order_confirmed_email(instance)
        
        #* Send completion email
        elif instance.state == 'completed':
            send_completion_email(instance)
    
    #* Send final price email when set
    elif hasattr(instance, '_final_price_set') and instance._final_price_set:
        send_final_price_email(instance)

#? <|--------------Email Helper Functions--------------|>

def send_order_confirmation_email(order):
    """Send initial order confirmation email"""
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'order_items': order.items.all(),
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        html_message = render_to_string('emails/order_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"Order Confirmation - {order.order_number}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"Confirmation email sent for order {order.order_number}")
        return True
        
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False

def send_estimate_email(order):
    """Send estimate/quote email"""
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'order_items': order.items.all(),
            'estimated_price': order.estimaded_price,
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        html_message = render_to_string('emails/order_estimate.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"Quote Ready - Order {order.order_number}",
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

def send_order_confirmed_email(order):
    """Send email when customer confirms the order"""
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'final_price': order.final_price or order.estimaded_price,
            'estimated_days': order.estimated_completion_date_days,
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        html_message = render_to_string('emails/order_status.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"Order Confirmed - {order.order_number}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"Confirmation email sent for order {order.order_number}")
        return True
        
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False

def send_final_price_email(order):
    """Send email with final price"""
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        html_message = render_to_string('emails/order_final_price.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"Final Price Ready - Order {order.order_number}",
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

def send_completion_email(order):
    """Send email when order is completed"""
    try:
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        }
        
        #* Note: The template name has a typo in your files (order_comleted.html)
        #* You should rename it to order_completed.html
        html_message = render_to_string('emails/order_completed.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"Order Completed! - {order.order_number}",
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