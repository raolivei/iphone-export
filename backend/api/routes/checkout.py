"""Checkout API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from backend.db.database import get_db
from backend.db.models import Order, OrderItem, Product, Inventory, OrderStatus, PaymentMethod
from backend.models.order import CheckoutRequest, OrderResponse
from backend.app.config import get_settings
from backend.services.payment import PaymentService
from backend.services.email import EmailService

router = APIRouter()
settings = get_settings()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_checkout(
    checkout_data: CheckoutRequest,
    db: Session = Depends(get_db)
):
    """Create a new order from checkout."""
    
    # Validate products and check inventory
    subtotal = 0.0
    order_items_data = []
    
    for item in checkout_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )
        
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.name} is not available"
            )
        
        # Check inventory
        inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
        if not inventory or inventory.quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Available: {inventory.quantity if inventory else 0}"
            )
        
        item_total = product.price_cad * item.quantity
        subtotal += item_total
        order_items_data.append({
            "product": product,
            "quantity": item.quantity,
            "price": product.price_cad
        })
    
    # Calculate shipping
    shipping_cost = settings.SHIPPING_COST_CAD
    total = subtotal + shipping_cost
    
    # Generate order number
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    # Create order
    order = Order(
        order_number=order_number,
        status=OrderStatus.PENDING,
        payment_method=checkout_data.payment_method,
        customer_name=checkout_data.shipping_address.name,
        customer_email=checkout_data.shipping_address.email,
        customer_phone=checkout_data.shipping_address.phone,
        shipping_address_line1=checkout_data.shipping_address.address_line1,
        shipping_address_line2=checkout_data.shipping_address.address_line2,
        shipping_city=checkout_data.shipping_address.city,
        shipping_state=checkout_data.shipping_address.state,
        shipping_postal_code=checkout_data.shipping_address.postal_code,
        shipping_country=checkout_data.shipping_address.country,
        subtotal_cad=subtotal,
        shipping_cost_cad=shipping_cost,
        total_cad=total,
    )
    
    db.add(order)
    db.flush()  # Get order ID
    
    # Create order items
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            price_cad=item_data["price"]
        )
        db.add(order_item)
    
    # Reserve inventory (will be confirmed on payment)
    # For now, we'll deduct immediately. In production, you might want to reserve first
    for item_data in order_items_data:
        inventory = db.query(Inventory).filter(Inventory.product_id == item_data["product"].id).first()
        if inventory:
            inventory.quantity -= item_data["quantity"]
            db.commit()
    
    db.commit()
    db.refresh(order)
    
    # Send order confirmation email
    try:
        email_service = EmailService()
        await email_service.send_order_confirmation(order, db)
    except Exception:
        # Silently fail - don't block order creation
        pass
    
    # Get order items for response
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    item_responses = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        item_responses.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": product.name if product else "Unknown",
            "quantity": item.quantity,
            "price_cad": item.price_cad,
            "subtotal_cad": item.quantity * item.price_cad,
        })
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        status=order.status,
        payment_method=order.payment_method,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        shipping_address_line1=order.shipping_address_line1,
        shipping_address_line2=order.shipping_address_line2,
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        shipping_postal_code=order.shipping_postal_code,
        shipping_country=order.shipping_country,
        subtotal_cad=order.subtotal_cad,
        shipping_cost_cad=order.shipping_cost_cad,
        total_cad=order.total_cad,
        tracking_number=order.tracking_number,
        items=item_responses,
        created_at=order.created_at,
        updated_at=order.updated_at,
        shipped_at=order.shipped_at,
        delivered_at=order.delivered_at,
    )


@router.post("/{order_id}/payment-confirm")
async def confirm_payment(
    order_id: int,
    payment_id: str,
    db: Session = Depends(get_db)
):
    """Confirm payment for an order (called by webhook)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    
    order.payment_id = payment_id
    order.status = OrderStatus.PAID
    db.commit()
    
    # Send payment confirmation email
    try:
        email_service = EmailService()
        await email_service.send_payment_confirmation(order, db)
    except Exception:
        pass
    
    return {"message": "Payment confirmed", "order_id": order_id}

