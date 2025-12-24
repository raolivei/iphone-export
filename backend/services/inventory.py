"""Inventory management service."""
from sqlalchemy.orm import Session
from backend.db.models import Inventory, Product
from backend.app.config import get_settings

settings = get_settings()


class InventoryService:
    """Service for managing inventory."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_stock(self, product_id: int) -> int:
        """Get current stock for a product."""
        inventory = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
        return inventory.quantity if inventory else 0
    
    def check_stock(self, product_id: int, quantity: int) -> bool:
        """Check if sufficient stock is available."""
        inventory = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            return False
        return inventory.quantity >= quantity
    
    def deduct_stock(self, product_id: int, quantity: int) -> bool:
        """Deduct stock from inventory."""
        inventory = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
        
        if not inventory:
            return False
        
        if inventory.quantity < quantity:
            return False
        
        inventory.quantity -= quantity
        self.db.commit()
        return True
    
    def add_stock(self, product_id: int, quantity: int) -> bool:
        """Add stock to inventory."""
        inventory = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
        
        if not inventory:
            # Create inventory record if it doesn't exist
            inventory = Inventory(
                product_id=product_id,
                quantity=quantity,
                low_stock_threshold=5
            )
            self.db.add(inventory)
        else:
            inventory.quantity += quantity
        
        self.db.commit()
        return True
    
    def set_stock(self, product_id: int, quantity: int) -> bool:
        """Set stock to a specific quantity."""
        inventory = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
        
        if not inventory:
            inventory = Inventory(
                product_id=product_id,
                quantity=quantity,
                low_stock_threshold=5
            )
            self.db.add(inventory)
        else:
            inventory.quantity = quantity
        
        self.db.commit()
        return True
    
    def get_low_stock_products(self) -> list:
        """Get list of products with low stock."""
        low_stock = self.db.query(Inventory).join(Product).filter(
            Inventory.quantity <= Inventory.low_stock_threshold,
            Product.is_active == True
        ).all()
        
        return [
            {
                "product_id": inv.product_id,
                "product_name": inv.product.name,
                "quantity": inv.quantity,
                "low_stock_threshold": inv.low_stock_threshold,
            }
            for inv in low_stock
        ]
    
    def get_out_of_stock_products(self) -> list:
        """Get list of out of stock products."""
        out_of_stock = self.db.query(Inventory).join(Product).filter(
            Inventory.quantity <= 0,
            Product.is_active == True
        ).all()
        
        return [
            {
                "product_id": inv.product_id,
                "product_name": inv.product.name,
                "quantity": inv.quantity,
            }
            for inv in out_of_stock
        ]





