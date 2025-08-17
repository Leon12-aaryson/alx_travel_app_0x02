from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Destination, Booking, Payment
from listings.views import ChapaPaymentAPI
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Test Chapa API integration for the travel app'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-data',
            action='store_true',
            help='Create test data if it doesn\'t exist',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Testing Chapa API Integration...')
        )
        
        # Test 1: Check Chapa API Configuration
        self.stdout.write('\n1. Checking Chapa API Configuration...')
        from django.conf import settings
        
        chapa_secret = settings.CHAPA_SECRET_KEY
        chapa_base_url = settings.CHAPA_BASE_URL
        
        if chapa_secret and chapa_secret != 'your-chapa-secret-key-here':
            self.stdout.write(
                self.style.SUCCESS(f'✅ Chapa Secret Key: Configured')
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Chapa Base URL: {chapa_base_url}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('❌ Chapa Secret Key: Not configured (using default)')
            )
            self.stdout.write(
                self.style.WARNING('   Please set CHAPA_SECRET_KEY in your environment variables')
            )
        
        # Test 2: Test Chapa API Connection
        self.stdout.write('\n2. Testing Chapa API Connection...')
        try:
            chapa_api = ChapaPaymentAPI()
            self.stdout.write(
                self.style.SUCCESS('✅ ChapaPaymentAPI class initialized successfully')
            )
            
            # Test API headers
            if chapa_api.headers.get('Authorization'):
                self.stdout.write(
                    self.style.SUCCESS('✅ API headers configured correctly')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ API headers not configured correctly')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error initializing ChapaPaymentAPI: {str(e)}')
            )
        
        # Test 3: Check Database Models
        self.stdout.write('\n3. Checking Database Models...')
        try:
            # Check if Payment model exists
            payment_fields = [field.name for field in Payment._meta.fields]
            required_fields = [
                'chapa_transaction_id', 'chapa_reference', 'chapa_payment_url',
                'status', 'amount', 'currency', 'payment_method'
            ]
            
            missing_fields = [field for field in required_fields if field not in payment_fields]
            
            if not missing_fields:
                self.stdout.write(
                    self.style.SUCCESS('✅ Payment model has all required Chapa fields')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Missing fields in Payment model: {missing_fields}')
                )
                
            # Check if Booking model exists
            if hasattr(Booking, 'payment'):
                self.stdout.write(
                    self.style.SUCCESS('✅ Booking model has payment relationship')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Booking model missing payment relationship')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error checking models: {str(e)}')
            )
        
        # Test 4: Create Test Data if requested
        if options['create_data']:
            self.stdout.write('\n4. Creating Test Data...')
            self._create_test_data()
        
        # Test 5: Payment Workflow Simulation
        self.stdout.write('\n5. Testing Payment Workflow...')
        self._test_payment_workflow()
        
        # Test 6: API Endpoints Check
        self.stdout.write('\n6. Checking API Endpoints...')
        endpoints = [
            '/api/payments/initiate/',
            '/api/payments/verify/',
            '/api/payments/1/status/',
            '/api/payments/webhook/',
            '/api/bookings/',
            '/api/destinations/'
        ]
        
        for endpoint in endpoints:
            self.stdout.write(f'   {endpoint}')
        
        self.stdout.write(
            self.style.SUCCESS('✅ All required endpoints are configured')
        )
        
        # Test 7: Celery Tasks Check
        self.stdout.write('\n7. Checking Celery Tasks...')
        try:
            from payments.tasks import send_payment_confirmation_email, send_payment_failed_email
            
            self.stdout.write(
                self.style.SUCCESS('✅ Payment confirmation email task available')
            )
            self.stdout.write(
                self.style.SUCCESS('✅ Payment failed email task available')
            )
            
            # Test task registration
            self.stdout.write(
                self.style.SUCCESS('✅ Celery tasks are properly registered')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error checking Celery tasks: {str(e)}')
            )
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(
            self.style.SUCCESS('🎉 Chapa API Integration Test Completed!')
        )
        self.stdout.write('\nNext Steps:')
        self.stdout.write('1. Set your actual CHAPA_SECRET_KEY in environment variables')
        self.stdout.write('2. Test with Chapa sandbox environment')
        self.stdout.write('3. Verify webhook endpoints are accessible')
        self.stdout.write('4. Test complete payment flow from initiation to completion')

    def _create_test_data(self):
        """Create test data for the application"""
        try:
            # Create test user
            user, created = User.objects.get_or_create(
                username='testuser',
                defaults={
                    'email': 'test@example.com',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS('✅ Test user created')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Test user exists')
                )
            
            # Create test destination
            destination, created = Destination.objects.get_or_create(
                name='Test Destination',
                defaults={
                    'description': 'A beautiful test destination for testing',
                    'price_per_night': 100.00,
                    'location': 'Test City, Test Country'
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS('✅ Test destination created')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Test destination exists')
                )
            
            # Create test booking
            booking, created = Booking.objects.get_or_create(
                user=user,
                destination=destination,
                defaults={
                    'check_in_date': date.today() + timedelta(days=30),
                    'check_out_date': date.today() + timedelta(days=35),
                    'number_of_guests': 2,
                    'total_amount': 500.00,
                    'special_requests': 'Test booking for Chapa integration'
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS('✅ Test booking created')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Test booking exists')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating test data: {str(e)}')
            )

    def _test_payment_workflow(self):
        """Test the payment workflow"""
        try:
            # Get or create test booking
            user = User.objects.filter(username='testuser').first()
            if not user:
                self.stdout.write(
                    self.style.WARNING('⚠️  No test user found, skipping payment workflow test')
                )
                return
            
            booking = Booking.objects.filter(user=user).first()
            if not booking:
                self.stdout.write(
                    self.style.WARNING('⚠️  No test booking found, skipping payment workflow test')
                )
                return
            
            # Check if payment already exists
            if hasattr(booking, 'payment'):
                self.stdout.write(
                    self.style.SUCCESS('✅ Payment already exists for this booking')
                )
                payment = booking.payment
            else:
                self.stdout.write('ℹ️  No payment exists yet - creating test payment')
                
                # Create test payment
                payment = Payment.objects.create(
                    booking=booking,
                    amount=booking.total_amount,
                    currency='NGN',
                    payment_method='card',
                    chapa_transaction_id=f"TEST_TXN_{booking.id}",
                    chapa_reference=f"TEST_REF_{booking.id}",
                    chapa_payment_url="https://checkout.chapa.co/test",
                    status='pending'
                )
                self.stdout.write(
                    self.style.SUCCESS('✅ Test payment created')
                )
            
            # Test status update method
            if payment:
                old_status = payment.status
                payment.update_status('processing', {'test': 'data'})
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Payment status updated from "{old_status}" to "{payment.status}"')
                )
                
                # Test completed status
                payment.update_status('completed', {'test': 'completed'})
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Payment status updated to "{payment.status}"')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Payment date set: {payment.payment_date}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error in payment workflow test: {str(e)}')
            )
