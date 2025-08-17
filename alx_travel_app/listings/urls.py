from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # Destination endpoints
    path('destinations/', views.DestinationListCreateView.as_view(), name='destination-list-create'),
    path('destinations/<int:pk>/', views.DestinationDetailView.as_view(), name='destination-detail'),
    
    # Booking endpoints
    path('bookings/', views.BookingListCreateView.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    
    # Review endpoints
    path('reviews/', views.ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    
    # Payment endpoints
    path('payments/initiate/', views.initiate_payment, name='initiate-payment'),
    path('payments/verify/', views.verify_payment, name='verify-payment'),
    path('payments/<int:payment_id>/status/', views.payment_status, name='payment-status'),
    path('payments/webhook/', views.chapa_webhook, name='chapa-webhook'),
]
