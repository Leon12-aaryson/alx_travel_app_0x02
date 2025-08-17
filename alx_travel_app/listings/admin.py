from django.contrib import admin
from .models import Destination, Booking, Payment, Review


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'price_per_night', 'created_at']
    list_filter = ['location', 'created_at']
    search_fields = ['name', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'user', 'destination', 'check_in_date', 'check_out_date', 'status', 'total_amount']
    list_filter = ['status', 'check_in_date', 'check_out_date', 'created_at']
    search_fields = ['booking_reference', 'user__username', 'destination__name']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']
    date_hierarchy = 'check_in_date'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'currency', 'status', 'payment_method', 'chapa_transaction_id', 'created_at']
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['chapa_transaction_id', 'chapa_reference', 'booking__booking_reference']
    readonly_fields = ['created_at', 'updated_at', 'payment_date']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('booking', 'amount', 'currency', 'payment_method', 'status')
        }),
        ('Chapa API Details', {
            'fields': ('chapa_transaction_id', 'chapa_reference', 'chapa_payment_url')
        }),
        ('Payment Details', {
            'fields': ('verification_response', 'payment_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'destination', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'destination__name', 'comment']
    readonly_fields = ['created_at', 'updated_at']
