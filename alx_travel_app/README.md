# ALX Travel App with Chapa API Integration

A Django-based travel booking application with integrated Chapa payment processing API.

## Features

- **Travel Destinations**: Browse and view travel destinations with pricing
- **Booking System**: Create and manage travel bookings
- **Chapa Payment Integration**: Secure payment processing using Chapa API
- **Payment Workflow**: Complete payment lifecycle from initiation to verification
- **Email Notifications**: Automated payment confirmation emails using Celery
- **RESTful API**: Full API endpoints for all functionality
- **Admin Interface**: Comprehensive admin panel for managing bookings and payments

## Chapa API Integration

This project integrates the Chapa API for handling payments, allowing users to make bookings with secure payment options. The integration includes:

### Payment Flow

1. **Payment Initiation**: When a user creates a booking, the system initiates payment via Chapa API
2. **Payment Processing**: Users are redirected to Chapa's secure payment page
3. **Payment Verification**: System verifies payment status with Chapa after completion
4. **Status Updates**: Payment and booking statuses are updated based on verification results
5. **Email Notifications**: Confirmation emails are sent upon successful payment

### Chapa API Endpoints Used

- `POST /v1/transaction/initialize` - Initialize payment
- `GET /v1/transaction/verify/{id}` - Verify payment status
- Webhook support for real-time payment notifications

## Project Structure

```
alx_travel_app/
├── core/                   # Django project settings
│   ├── settings.py        # Main settings with Chapa configuration
│   ├── urls.py           # Main URL configuration
│   ├── wsgi.py           # WSGI configuration
│   ├── asgi.py           # ASGI configuration
│   └── celery.py         # Celery configuration
├── listings/              # Main app for destinations, bookings, payments
│   ├── models.py         # Database models including Payment model
│   ├── views.py          # API views with Chapa integration
│   ├── serializers.py    # API serializers
│   ├── urls.py           # App URL patterns
│   └── admin.py          # Admin interface configuration
├── payments/              # Payment-specific functionality
│   ├── views.py          # Payment success/failure views
│   ├── tasks.py          # Celery background tasks
│   └── urls.py           # Payment URL patterns
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
└── README.md             # This file
```

## Models

### Payment Model

The `Payment` model stores all payment-related information:

- **Basic Fields**: amount, currency, payment method, status
- **Chapa API Fields**: transaction ID, reference, payment URL
- **Verification Fields**: response data, payment date
- **Status Management**: Methods to update payment status

### Booking Model

The `Booking` model manages travel bookings:

- **User Association**: Links to authenticated users
- **Destination**: References travel destinations
- **Payment Relationship**: One-to-one relationship with Payment model
- **Status Tracking**: Tracks booking confirmation status

## API Endpoints

### Payment Endpoints

- `POST /api/payments/initiate/` - Initiate payment for a booking
- `POST /api/payments/verify/` - Verify payment status with Chapa
- `GET /api/payments/{id}/status/` - Get payment status
- `POST /api/payments/webhook/` - Chapa webhook endpoint

### Booking Endpoints

- `GET /api/bookings/` - List user's bookings
- `POST /api/bookings/` - Create new booking
- `GET /api/bookings/{id}/` - Get booking details
- `PUT /api/bookings/{id}/` - Update booking
- `DELETE /api/bookings/{id}/` - Cancel booking

### Destination Endpoints

- `GET /api/destinations/` - List all destinations
- `POST /api/destinations/` - Create destination (admin only)
- `GET /api/destinations/{id}/` - Get destination details
- `PUT /api/destinations/{id}/` - Update destination
- `DELETE /api/destinations/{id}/` - Delete destination

## Setup Instructions

### 1. Clone and Setup

```bash
git clone <repository-url>
cd alx_travel_app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp env.example .env
# Edit .env with your actual values
```

**Required Environment Variables:**

- `CHAPA_SECRET_KEY`: Your Chapa API secret key
- `CHAPA_BASE_URL`: Chapa API base URL (https://api.chapa.co)
- `CHAPA_WEBHOOK_SECRET`: Webhook verification secret
- `EMAIL_HOST_USER`: Email address for sending notifications
- `EMAIL_HOST_PASSWORD`: Email password or app password

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

### 5. Start Celery Worker (Optional)

```bash
# Start Redis server first
redis-server

# Start Celery worker
celery -A core worker -l info
```

## Chapa API Setup

### 1. Create Chapa Account

1. Visit [Chapa Developer Portal](https://developer.chapa.co/)
2. Sign up for a developer account
3. Navigate to API Keys section
4. Generate your secret key

### 2. Configure Webhooks

1. Set webhook URL in Chapa dashboard: `https://yourdomain.com/api/payments/webhook/`
2. Configure webhook events for payment notifications
3. Note your webhook secret for verification

### 3. Test Integration

1. Use Chapa's sandbox environment for testing
2. Test payment initiation and verification flows
3. Verify webhook notifications are received

## Payment Workflow

### 1. User Creates Booking

```python
# User submits booking form
POST /api/bookings/
{
    "destination_id": 1,
    "check_in_date": "2024-01-15",
    "check_out_date": "2024-01-20",
    "number_of_guests": 2,
    "special_requests": "Early check-in preferred"
}
```

### 2. Initiate Payment

```python
# System initiates payment with Chapa
POST /api/payments/initiate/
{
    "booking_id": 1,
    "payment_method": "card",
    "currency": "NGN"
}
```

### 3. User Completes Payment

- User is redirected to Chapa payment page
- Completes payment using preferred method
- Chapa redirects back to success/failure URL

### 4. Payment Verification

```python
# System verifies payment with Chapa
POST /api/payments/verify/
{
    "transaction_id": "chapa_transaction_id"
}
```

### 5. Status Updates

- Payment status updated to 'completed'
- Booking status updated to 'confirmed'
- Confirmation email sent via Celery

## Testing

### Sandbox Testing

1. Use Chapa's sandbox environment for development
2. Test with sandbox API keys
3. Verify payment flows work correctly

### API Testing

Use tools like Postman or curl to test endpoints:

```bash
# Test payment initiation
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"booking_id": 1, "payment_method": "card"}'
```

## Security Considerations

- **API Keys**: Store Chapa API keys in environment variables
- **Webhook Verification**: Implement proper webhook signature verification
- **HTTPS**: Use HTTPS in production for secure communication
- **Input Validation**: Validate all payment data before processing

## Production Deployment

### 1. Environment Variables

- Set `DEBUG=False`
- Configure production database
- Use production Chapa API keys
- Set proper `ALLOWED_HOSTS`

### 2. Webhook Configuration

- Update webhook URLs to production domain
- Implement webhook signature verification
- Monitor webhook delivery and failures

### 3. Monitoring

- Monitor payment success/failure rates
- Track API response times
- Set up error alerting for failed payments

## Troubleshooting

### Common Issues

1. **Payment Initiation Fails**
   - Check Chapa API key configuration
   - Verify API endpoint URLs
   - Check network connectivity

2. **Webhook Not Received**
   - Verify webhook URL configuration
   - Check server accessibility
   - Review webhook event settings

3. **Payment Verification Fails**
   - Verify transaction ID format
   - Check Chapa API response
   - Review error logging

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'listings': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Support

For issues related to:
- **Chapa API**: Contact Chapa support
- **Django Application**: Check Django documentation
- **Payment Integration**: Review API documentation and logs

## License

This project is part of the ALX Software Engineering program.
