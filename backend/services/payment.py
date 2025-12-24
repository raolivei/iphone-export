"""Payment processing service for Stripe and PayPal."""
import stripe
import paypalrestsdk
from typing import Optional, Dict
from backend.app.config import get_settings
from backend.db.models import Order, PaymentMethod

settings = get_settings()

# Initialize Stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

# Initialize PayPal
if settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET:
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET
    })


class PaymentService:
    """Service for processing payments."""
    
    @staticmethod
    def create_stripe_payment_intent(order: Order) -> Dict:
        """Create a Stripe payment intent."""
        if not settings.STRIPE_SECRET_KEY:
            raise ValueError("Stripe secret key not configured")
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_cad * 100),  # Convert to cents
                currency="cad",
                metadata={
                    "order_id": order.id,
                    "order_number": order.order_number,
                },
            )
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
            }
        except Exception as e:
            raise Exception(f"Failed to create Stripe payment intent: {str(e)}")
    
    @staticmethod
    def verify_stripe_webhook(payload: bytes, signature: str) -> Dict:
        """Verify Stripe webhook signature."""
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise ValueError("Stripe webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            raise ValueError(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise ValueError(f"Invalid signature: {str(e)}")
    
    @staticmethod
    def create_paypal_payment(order: Order) -> Dict:
        """Create a PayPal payment."""
        if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
            raise ValueError("PayPal credentials not configured")
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": f"{order.total_cad:.2f}",
                    "currency": "CAD"
                },
                "description": f"Order {order.order_number}",
                "custom": str(order.id),
            }],
            "redirect_urls": {
                "return_url": "http://localhost:3004/checkout/success",
                "cancel_url": "http://localhost:3004/checkout/cancel"
            }
        })
        
        if payment.create():
            return {
                "payment_id": payment.id,
                "approval_url": next(link.href for link in payment.links if link.rel == "approval_url"),
            }
        else:
            raise Exception(f"PayPal payment creation failed: {payment.error}")
    
    @staticmethod
    def execute_paypal_payment(payment_id: str, payer_id: str) -> Dict:
        """Execute a PayPal payment."""
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            return {
                "payment_id": payment.id,
                "state": payment.state,
                "transaction_id": payment.transactions[0].related_resources[0].sale.id,
            }
        else:
            raise Exception(f"PayPal payment execution failed: {payment.error}")
    
    @staticmethod
    def verify_paypal_webhook(headers: Dict, body: str) -> Dict:
        """Verify PayPal webhook (simplified - in production use proper verification)."""
        # In production, verify webhook signature with PayPal
        # For now, return the parsed body
        import json
        try:
            return json.loads(body)
        except:
            raise ValueError("Invalid PayPal webhook payload")





