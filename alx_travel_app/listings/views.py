import requests
import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Destination, Booking, Payment, Review
from .serializers import (
    DestinationSerializer, BookingSerializer, ReviewSerializer,
    PaymentInitiationSerializer, PaymentVerificationSerializer
)

logger = logging.getLogger(__name__)


class ChapaPaymentAPI:
    """Class to handle Chapa API interactions"""
    
    def __init__(self):
        self.secret_key = settings.CHAPA_SECRET_KEY
        self.base_url = settings.CHAPA_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def initiate_payment(self, booking, payment_method, currency='NGN'):
        """Initiate payment with Chapa API"""
        try:
            # Prepare payment data for Chapa
            payment_data = {
                'amount': str(booking.total_amount),
                'currency': currency,
                'email': booking.user.email,
                'first_name': booking.user.first_name or booking.user.username,
                'last_name': booking.user.last_name or '',
                'tx_ref': f"TRAVEL_{booking.booking_reference}_{booking.id}",
                'callback_url': f"{settings.CHAPA_BASE_URL}/api/payments/webhook/",
                'return_url': f"{settings.CHAPA_BASE_URL}/api/payments/success/",
                'customization': {
                    'title': f"Travel Booking - {booking.destination.name}",
                    'description': f"Payment for {booking.destination.name} booking"
                }
            }
            
            # Make request to Chapa API
            response = requests.post(
                f"{self.base_url}/v1/transaction/initialize",
                headers=self.headers,
                json=payment_data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return {
                    'success': True,
                    'data': response_data,
                    'payment_url': response_data.get('data', {}).get('checkout_url'),
                    'reference': response_data.get('data', {}).get('reference'),
                    'transaction_id': response_data.get('data', {}).get('id')
                }
            else:
                logger.error(f"Chapa API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Chapa API error: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            logger.error(f"Error initiating payment: {str(e)}")
            return {
                'success': False,
                'error': f"Payment initiation failed: {str(e)}"
            }
    
    def verify_payment(self, transaction_id):
        """Verify payment status with Chapa API"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/transaction/verify/{transaction_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return {
                    'success': True,
                    'data': response_data,
                    'status': response_data.get('data', {}).get('status'),
                    'amount': response_data.get('data', {}).get('amount'),
                    'currency': response_data.get('data', {}).get('currency')
                }
            else:
                logger.error(f"Chapa verification error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Verification failed: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return {
                'success': False,
                'error': f"Payment verification failed: {str(e)}"
            }


class DestinationListCreateView(ListCreateAPIView):
    """View for listing and creating destinations"""
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated]


class DestinationDetailView(RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting destinations"""
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated]


class BookingListCreateView(ListCreateAPIView):
    """View for listing and creating bookings"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class BookingDetailView(RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting bookings"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class ReviewListCreateView(ListCreateAPIView):
    """View for listing and creating reviews"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)


class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting reviews"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """API endpoint to initiate payment with Chapa"""
    serializer = PaymentInitiationSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        try:
            booking = get_object_or_404(Booking, id=serializer.validated_data['booking_id'])
            
            # Check if payment already exists
            if hasattr(booking, 'payment'):
                return Response({
                    'error': 'Payment already exists for this booking'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Initialize Chapa payment
            chapa_api = ChapaPaymentAPI()
            payment_result = chapa_api.initiate_payment(
                booking=booking,
                payment_method=serializer.validated_data['payment_method'],
                currency=serializer.validated_data['currency']
            )
            
            if payment_result['success']:
                # Create payment record
                payment = Payment.objects.create(
                    booking=booking,
                    amount=booking.total_amount,
                    currency=serializer.validated_data['currency'],
                    payment_method=serializer.validated_data['payment_method'],
                    chapa_transaction_id=payment_result['transaction_id'],
                    chapa_reference=payment_result['reference'],
                    chapa_payment_url=payment_result['payment_url'],
                    status='pending'
                )
                
                return Response({
                    'message': 'Payment initiated successfully',
                    'payment_id': payment.id,
                    'payment_url': payment.chapa_payment_url,
                    'transaction_id': payment.chapa_transaction_id,
                    'reference': payment.chapa_reference
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': 'Failed to initiate payment',
                    'details': payment_result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in payment initiation: {str(e)}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """API endpoint to verify payment with Chapa"""
    serializer = PaymentVerificationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            transaction_id = serializer.validated_data['transaction_id']
            payment = get_object_or_404(Payment, chapa_transaction_id=transaction_id)
            
            # Verify payment with Chapa
            chapa_api = ChapaPaymentAPI()
            verification_result = chapa_api.verify_payment(transaction_id)
            
            if verification_result['success']:
                chapa_status = verification_result['status']
                
                # Update payment status based on Chapa response
                if chapa_status == 'success':
                    payment.update_status('completed', verification_result['data'])
                    # Update booking status
                    payment.booking.status = 'confirmed'
                    payment.booking.save()
                    
                    # TODO: Send confirmation email using Celery
                    # send_payment_confirmation_email.delay(payment.id)
                    
                    return Response({
                        'message': 'Payment verified successfully',
                        'status': 'completed',
                        'payment_id': payment.id
                    }, status=status.HTTP_200_OK)
                    
                elif chapa_status == 'failed':
                    payment.update_status('failed', verification_result['data'])
                    return Response({
                        'message': 'Payment verification failed',
                        'status': 'failed',
                        'payment_id': payment.id
                    }, status=status.HTTP_200_OK)
                    
                else:
                    payment.update_status('processing', verification_result['data'])
                    return Response({
                        'message': 'Payment is being processed',
                        'status': 'processing',
                        'payment_id': payment.id
                    }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Payment verification failed',
                    'details': verification_result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in payment verification: {str(e)}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, payment_id):
    """API endpoint to get payment status"""
    try:
        payment = get_object_or_404(Payment, id=payment_id, booking__user=request.user)
        return Response({
            'payment_id': payment.id,
            'status': payment.status,
            'amount': payment.amount,
            'currency': payment.currency,
            'transaction_id': payment.chapa_transaction_id,
            'payment_date': payment.payment_date,
            'created_at': payment.created_at
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chapa_webhook(request):
    """Webhook endpoint for Chapa payment notifications"""
    try:
        # Verify webhook signature (implement proper verification in production)
        webhook_data = request.data
        
        # Extract transaction details
        transaction_id = webhook_data.get('id')
        status = webhook_data.get('status')
        
        if transaction_id and status:
            try:
                payment = Payment.objects.get(chapa_transaction_id=transaction_id)
                
                # Update payment status based on webhook
                if status == 'success':
                    payment.update_status('completed', webhook_data)
                    payment.booking.status = 'confirmed'
                    payment.booking.save()
                    
                    # TODO: Send confirmation email using Celery
                    # send_payment_confirmation_email.delay(payment.id)
                    
                elif status == 'failed':
                    payment.update_status('failed', webhook_data)
                
                return Response({'status': 'success'}, status=status.HTTP_200_OK)
                
            except Payment.DoesNotExist:
                logger.warning(f"Payment not found for transaction ID: {transaction_id}")
                return Response({'status': 'payment_not_found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'status': 'invalid_webhook'}, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
