from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from listings.models import Payment
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_payment_confirmation_email(payment_id):
    """Send payment confirmation email to user"""
    try:
        payment = Payment.objects.get(id=payment_id)
        user = payment.booking.user
        destination = payment.booking.destination
        
        subject = f"Payment Confirmed - {destination.name} Booking"
        
        # Email content
        message = f"""
        Dear {user.get_full_name() or user.username},
        
        Your payment for the {destination.name} booking has been confirmed!
        
        Booking Details:
        - Booking Reference: {payment.booking.booking_reference}
        - Destination: {destination.name}
        - Check-in: {payment.booking.check_in_date}
        - Check-out: {payment.booking.check_out_date}
        - Amount Paid: {payment.currency} {payment.amount}
        - Transaction ID: {payment.chapa_transaction_id}
        
        Thank you for choosing our travel service!
        
        Best regards,
        ALX Travel Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER or 'noreply@alxtravel.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Payment confirmation email sent to {user.email}")
        return True
        
    except Payment.DoesNotExist:
        logger.error(f"Payment with ID {payment_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error sending payment confirmation email: {str(e)}")
        return False


@shared_task
def send_payment_failed_email(payment_id):
    """Send payment failed notification email to user"""
    try:
        payment = Payment.objects.get(id=payment_id)
        user = payment.booking.user
        destination = payment.booking.destination
        
        subject = f"Payment Failed - {destination.name} Booking"
        
        message = f"""
        Dear {user.get_full_name() or user.username},
        
        Unfortunately, your payment for the {destination.name} booking has failed.
        
        Booking Details:
        - Booking Reference: {payment.booking.booking_reference}
        - Destination: {destination.name}
        - Amount: {payment.currency} {payment.amount}
        
        Please try again or contact our support team for assistance.
        
        Best regards,
        ALX Travel Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER or 'noreply@alxtravel.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Payment failed email sent to {user.email}")
        return True
        
    except Payment.DoesNotExist:
        logger.error(f"Payment with ID {payment_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error sending payment failed email: {str(e)}")
        return False


@shared_task
def process_payment_webhook(webhook_data):
    """Process payment webhook data from Chapa"""
    try:
        transaction_id = webhook_data.get('id')
        status = webhook_data.get('status')
        
        if not transaction_id or not status:
            logger.warning("Invalid webhook data received")
            return False
            
        # This task can be used to process webhooks asynchronously
        # if needed for complex processing
        logger.info(f"Processing webhook for transaction {transaction_id} with status {status}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing payment webhook: {str(e)}")
        return False
