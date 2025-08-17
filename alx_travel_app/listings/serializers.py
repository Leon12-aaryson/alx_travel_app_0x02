from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Destination, Booking, Payment, Review


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'currency', 'payment_method', 'status',
            'chapa_transaction_id', 'chapa_reference', 'chapa_payment_url',
            'payment_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'chapa_transaction_id', 'chapa_reference', 'chapa_payment_url',
            'payment_date', 'created_at', 'updated_at'
        ]


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    destination = DestinationSerializer(read_only=True)
    destination_id = serializers.IntegerField(write_only=True)
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'destination', 'destination_id', 'check_in_date',
            'check_out_date', 'number_of_guests', 'total_amount', 'status',
            'booking_reference', 'special_requests', 'payment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'status', 'booking_reference', 'payment', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    destination = DestinationSerializer(read_only=True)
    destination_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'destination', 'destination_id', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PaymentInitiationSerializer(serializers.Serializer):
    """Serializer for initiating payment with Chapa API"""
    booking_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    currency = serializers.CharField(max_length=3, default='NGN')
    
    def validate_booking_id(self, value):
        try:
            booking = Booking.objects.get(id=value, user=self.context['request'].user)
            if booking.payment.exists():
                raise serializers.ValidationError("Payment already exists for this booking")
            return value
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Booking not found")


class PaymentVerificationSerializer(serializers.Serializer):
    """Serializer for verifying payment with Chapa API"""
    transaction_id = serializers.CharField(max_length=100)
    
    def validate_transaction_id(self, value):
        try:
            Payment.objects.get(chapa_transaction_id=value)
            return value
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Transaction ID not found")
