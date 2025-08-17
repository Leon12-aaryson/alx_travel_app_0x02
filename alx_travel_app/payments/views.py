from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def payment_success(request):
    """Handle successful payment redirect from Chapa"""
    return Response({
        'message': 'Payment completed successfully!',
        'status': 'success'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def payment_failed(request):
    """Handle failed payment redirect from Chapa"""
    return Response({
        'message': 'Payment failed. Please try again.',
        'status': 'failed'
    }, status=status.HTTP_400_BAD_REQUEST)
