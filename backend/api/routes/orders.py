"""Order API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.db.database import get_db
from backend.db.models import Order, OrderItem, OrderStatus, Product
from backend.models.order import OrderResponse, OrderUpdate, OrderListResponse
from sqlalchemy import desc

router = APIRouter()


@router.get("/", response_model=OrderListResponse)
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[OrderStatus] = None,
    db: Session = Depends(get_db)
):
    """List all orders."""
    query = db.query(Order)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    total = query.count()
    orders = query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    order_responses = []
    for order in orders:
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
        
        order_dict = {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "payment_method": order.payment_method,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "customer_phone": order.customer_phone,
            "shipping_address_line1": order.shipping_address_line1,
            "shipping_address_line2": order.shipping_address_line2,
            "shipping_city": order.shipping_city,
            "shipping_state": order.shipping_state,
            "shipping_postal_code": order.shipping_postal_code,
            "shipping_country": order.shipping_country,
            "subtotal_cad": order.subtotal_cad,
            "shipping_cost_cad": order.shipping_cost_cad,
            "total_cad": order.total_cad,
            "tracking_number": order.tracking_number,
            "items": item_responses,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "shipped_at": order.shipped_at,
            "delivered_at": order.delivered_at,
        }
        order_responses.append(OrderResponse(**order_dict))
    
    return OrderListResponse(orders=order_responses, total=total)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a single order by ID."""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    from backend.db.models import Product
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


@router.get("/by-number/{order_number}", response_model=OrderResponse)
async def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    """Get an order by order number."""
    order = db.query(Order).filter(Order.order_number == order_number).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with number {order_number} not found"
        )
    
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    from backend.db.models import Product
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

