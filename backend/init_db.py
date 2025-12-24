"""Initialize database with tables and seed data."""
from backend.db.database import engine, Base, SessionLocal
from backend.db.models import Product, Inventory, AdminUser
from backend.app.config import get_settings
from passlib.context import CryptContext
from datetime import datetime

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created")


def seed_data():
    """Seed database with initial data."""
    db = SessionLocal()
    
    try:
        # Create admin user
        admin = db.query(AdminUser).filter(AdminUser.username == settings.ADMIN_USERNAME).first()
        if not admin:
            hashed_password = pwd_context.hash(settings.ADMIN_PASSWORD)
            admin = AdminUser(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                hashed_password=hashed_password,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"Admin user created: {settings.ADMIN_USERNAME}")
        else:
            print(f"Admin user already exists: {settings.ADMIN_USERNAME}")
        
        # Create iPhone products
        products_data = [
            {
                "name": "iPhone 15 Pro 128GB",
                "description": "Latest iPhone 15 Pro with 128GB storage. Features A17 Pro chip, Pro camera system, and titanium design.",
                "price_cad": 1399.00,
                "image_url": "https://via.placeholder.com/400x400?text=iPhone+15+Pro+128GB",
                "specifications": "6.1-inch Super Retina XDR display, A17 Pro chip, 48MP Main camera, 128GB storage, Titanium design",
                "initial_stock": 5,
                "low_stock_threshold": 2,
            },
            {
                "name": "iPhone 15 Pro 256GB",
                "description": "Latest iPhone 15 Pro with 256GB storage. Features A17 Pro chip, Pro camera system, and titanium design.",
                "price_cad": 1599.00,
                "image_url": "https://via.placeholder.com/400x400?text=iPhone+15+Pro+256GB",
                "specifications": "6.1-inch Super Retina XDR display, A17 Pro chip, 48MP Main camera, 256GB storage, Titanium design",
                "initial_stock": 3,
                "low_stock_threshold": 2,
            },
            {
                "name": "iPhone 15 128GB",
                "description": "Latest iPhone 15 with 128GB storage. Features A16 Bionic chip and advanced camera system.",
                "price_cad": 1099.00,
                "image_url": "https://via.placeholder.com/400x400?text=iPhone+15+128GB",
                "specifications": "6.1-inch Super Retina XDR display, A16 Bionic chip, 48MP Main camera, 128GB storage",
                "initial_stock": 4,
                "low_stock_threshold": 2,
            },
        ]
        
        for product_data in products_data:
            existing = db.query(Product).filter(Product.name == product_data["name"]).first()
            if not existing:
                product = Product(
                    name=product_data["name"],
                    description=product_data["description"],
                    price_cad=product_data["price_cad"],
                    image_url=product_data["image_url"],
                    specifications=product_data["specifications"],
                    is_active=True,
                )
                db.add(product)
                db.flush()
                
                # Create inventory
                inventory = Inventory(
                    product_id=product.id,
                    quantity=product_data["initial_stock"],
                    low_stock_threshold=product_data["low_stock_threshold"],
                )
                db.add(inventory)
                db.commit()
                print(f"Product created: {product_data['name']}")
            else:
                print(f"Product already exists: {product_data['name']}")
        
        print("Seed data completed")
    
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Seeding data...")
    seed_data()
    print("Database initialization complete!")





