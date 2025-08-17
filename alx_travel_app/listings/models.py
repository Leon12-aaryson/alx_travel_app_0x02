from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Destination(models.Model):
    """Model for travel destinations"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='destinations/', null=True, blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Booking(models.Model):
    """Model for travel bookings"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_reference = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.destination.name}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = str(uuid.uuid4())
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class Payment(models.Model):
    """Model for storing payment-related information for Chapa API integration"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('crypto', 'Cryptocurrency'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Chapa API specific fields
    chapa_transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    chapa_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    chapa_payment_url = models.URLField(max_length=500, null=True, blank=True)
    
    # Payment verification fields
    verification_response = models.JSONField(null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.booking.booking_reference} - {self.status}"

    def update_status(self, new_status, chapa_response=None):
        """Update payment status and store Chapa response"""
        self.status = new_status
        if chapa_response:
            self.verification_response = chapa_response
        if new_status == 'completed':
            self.payment_date = timezone.now()
        self.save()

    class Meta:
        ordering = ['-created_at']


class Review(models.Model):
    """Model for destination reviews"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.destination.name}"

    class Meta:
        unique_together = ['user', 'destination']
        ordering = ['-created_at']
