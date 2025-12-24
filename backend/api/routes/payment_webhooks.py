"""Payment webhook routes for Stripe and PayPal."""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import Order, OrderStatus
from backend.services.payment import PaymentService
from backend.services.email import EmailService
import json

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header"
        )
    
    try:
        payment_service = PaymentService()
        event = payment_service.verify_stripe_webhook(payload, sig_header)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Handle different event types
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        order_id = payment_intent.get("metadata", {}).get("order_id")
        
        if order_id:
            order = db.query(Order).filter(Order.id == int(order_id)).first()
            if order:
                order.payment_id = payment_intent["id"]
                order.status = OrderStatus.PAID
                db.commit()
                
                # Send payment confirmation email
                try:
                    email_service = EmailService()
                    await email_service.send_payment_confirmation(order, db)
                except Exception:
                    pass
    
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        order_id = payment_intent.get("metadata", {}).get("order_id")
        
        if order_id:
            order = db.query(Order).filter(Order.id == int(order_id)).first()
            if order:
                order.status = OrderStatus.CANCELLED
                db.commit()
    
    return {"status": "success"}


@router.post("/paypal")
async def paypal_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle PayPal webhook events."""
    body = await request.body()
    headers = dict(request.headers)
    
    try:
        payment_service = PaymentService()
        event = payment_service.verify_paypal_webhook(headers, body.decode())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Handle PayPal webhook events
    event_type = event.get("event_type")
    
    if event_type == "PAYMENT.SALE.COMPLETED":
        # Payment completed
        resource = event.get("resource", {})
        custom = resource.get("custom")  # Should contain order_id
        
        if custom:
            order = db.query(Order).filter(Order.id == int(custom)).first()
            if order:
                order.payment_id = resource.get("id")
                order.status = OrderStatus.PAID
                db.commit()
                
                # Send payment confirmation email
                try:
                    email_service = EmailService()
                    await email_service.send_payment_confirmation(order, db)
                except Exception:
                    pass
    
    return {"status": "success"}





