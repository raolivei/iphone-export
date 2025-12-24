"""Product API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.db.database import get_db
from backend.db.models import Product, Inventory
from backend.models.product import ProductResponse, ProductCreate, ProductUpdate, ProductListResponse

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
async def list_products(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all products."""
    query = db.query(Product)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    
    # Add inventory information
    product_responses = []
    for product in products:
        inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
        product_dict = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price_cad": product.price_cad,
            "image_url": product.image_url,
            "specifications": product.specifications,
            "is_active": product.is_active,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "stock_quantity": inventory.quantity if inventory else 0,
            "is_in_stock": (inventory.quantity > 0) if inventory else False,
            "is_low_stock": (inventory.quantity <= inventory.low_stock_threshold) if inventory else False,
        }
        product_responses.append(ProductResponse(**product_dict))
    
    return ProductListResponse(products=product_responses, total=total)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        price_cad=product.price_cad,
        image_url=product.image_url,
        specifications=product.specifications,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
        stock_quantity=inventory.quantity if inventory else 0,
        is_in_stock=(inventory.quantity > 0) if inventory else False,
        is_low_stock=(inventory.quantity <= inventory.low_stock_threshold) if inventory else False,
    )





