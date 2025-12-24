"""Pydantic models for products."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Base product model."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price_cad: float = Field(..., gt=0)
    image_url: Optional[str] = None
    specifications: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    """Product creation model."""
    initial_stock: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)


class ProductUpdate(BaseModel):
    """Product update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price_cad: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = None
    specifications: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Product response model."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    stock_quantity: Optional[int] = None
    is_in_stock: Optional[bool] = None
    is_low_stock: Optional[bool] = None
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Product list response."""
    products: list[ProductResponse]
    total: int





