"""Pydantic models for orders."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from backend.db.models import OrderStatus, PaymentMethod


class ShippingAddress(BaseModel):
    """Shipping address model."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = None
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(default="Brazil", max_length=100)


class CartItem(BaseModel):
    """Cart item model."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=10)


class CheckoutRequest(BaseModel):
    """Checkout request model."""
    items: List[CartItem] = Field(..., min_length=1)
    shipping_address: ShippingAddress
    payment_method: PaymentMethod


class OrderItemResponse(BaseModel):
    """Order item response model."""
    id: int
    product_id: int
    product_name: str
    quantity: int
    price_cad: float
    subtotal_cad: float
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Order response model."""
    id: int
    order_number: str
    status: OrderStatus
    payment_method: Optional[PaymentMethod] = None
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address_line1: str
    shipping_address_line2: Optional[str] = None
    shipping_city: str
    shipping_state: str
    shipping_postal_code: str
    shipping_country: str
    subtotal_cad: float
    shipping_cost_cad: float
    total_cad: float
    tracking_number: Optional[str] = None
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    """Order update model."""
    status: Optional[OrderStatus] = None
    tracking_number: Optional[str] = None


class OrderListResponse(BaseModel):
    """Order list response."""
    orders: List[OrderResponse]
    total: int





