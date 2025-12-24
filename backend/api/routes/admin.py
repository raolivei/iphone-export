"""Admin API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from backend.db.database import get_db
from backend.db.models import Product, Order, Inventory, AdminUser, OrderStatus
from backend.models.product import ProductCreate, ProductUpdate, ProductResponse
from backend.models.order import OrderUpdate, OrderListResponse, OrderResponse
from backend.services.inventory import InventoryService
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from backend.app.config import get_settings

router = APIRouter()
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-change-in-production"  # Should be in settings
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_admin(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get current admin user from JWT token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found or inactive"
        )
    
    return admin


@router.post("/login")
async def admin_login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Admin login endpoint."""
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    
    if not admin or not verify_password(password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Update last login
    admin.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": admin.username})
    
    return {"access_token": access_token, "token_type": "bearer"}


# Product management
@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Create a new product."""
    product = Product(
        name=product_data.name,
        description=product_data.description,
        price_cad=product_data.price_cad,
        image_url=product_data.image_url,
        specifications=product_data.specifications,
        is_active=product_data.is_active,
    )
    db.add(product)
    db.flush()
    
    # Create inventory
    inventory = Inventory(
        product_id=product.id,
        quantity=product_data.initial_stock,
        low_stock_threshold=product_data.low_stock_threshold,
    )
    db.add(inventory)
    db.commit()
    db.refresh(product)
    
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
        stock_quantity=inventory.quantity,
        is_in_stock=inventory.quantity > 0,
        is_low_stock=inventory.quantity <= inventory.low_stock_threshold,
    )


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Update a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.price_cad is not None:
        product.price_cad = product_data.price_cad
    if product_data.image_url is not None:
        product.image_url = product_data.image_url
    if product_data.specifications is not None:
        product.specifications = product_data.specifications
    if product_data.is_active is not None:
        product.is_active = product_data.is_active
    
    db.commit()
    db.refresh(product)
    
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


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Delete a product (soft delete by setting is_active=False)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    product.is_active = False
    db.commit()
    
    return None


# Order management
@router.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Update an order (status, tracking number)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    
    if order_data.status is not None:
        order.status = order_data.status
        if order_data.status == OrderStatus.SHIPPED:
            order.shipped_at = datetime.utcnow()
        elif order_data.status == OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()
    
    if order_data.tracking_number is not None:
        order.tracking_number = order_data.tracking_number
    
    db.commit()
    db.refresh(order)
    
    # Get order items for response
    from backend.db.models import OrderItem
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


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get dashboard statistics."""
    total_products = db.query(Product).filter(Product.is_active == True).count()
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    paid_orders = db.query(Order).filter(Order.status == OrderStatus.PAID).count()
    
    # Low stock products
    low_stock_products = db.query(Inventory).join(Product).filter(
        Inventory.quantity <= Inventory.low_stock_threshold,
        Product.is_active == True
    ).count()
    
    # Total revenue
    total_revenue = db.query(Order).filter(
        Order.status.in_([OrderStatus.PAID, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).with_entities(db.func.sum(Order.total_cad)).scalar() or 0.0
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "paid_orders": paid_orders,
        "low_stock_products": low_stock_products,
        "total_revenue_cad": float(total_revenue),
    }





