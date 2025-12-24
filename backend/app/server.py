"""FastAPI application factory."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import get_settings
from backend.api.routes import products, orders, checkout, admin, payment_webhooks

settings = get_settings()


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    
    app = FastAPI(
        title="iPhone Export API",
        description="Ecommerce API for selling iPhones with international shipping",
        version="0.1.0",
        debug=settings.DEBUG,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(products.router, prefix="/api/products", tags=["products"])
    app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
    app.include_router(checkout.router, prefix="/api/checkout", tags=["checkout"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
    app.include_router(payment_webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "iPhone Export API",
            "version": "0.1.0",
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return app


app = create_app()

