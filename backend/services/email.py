"""Email service for sending notifications."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.config import get_settings
from backend.db.models import Order, OrderItem, Product

settings = get_settings()


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from = settings.SMTP_FROM
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send an email."""
        if not self.smtp_user or not self.smtp_password:
            return False
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_from
            msg["To"] = to_email
            
            if text_body:
                msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception:
            return False
    
    async def send_order_confirmation(self, order: Order, db: Session) -> bool:
        """Send order confirmation email to customer."""
        # Get order items
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        products = {}
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            products[item.id] = product.name if product else "Unknown"
        
        subject = f"Order Confirmation - {order.order_number}"
        
        html_body = f"""
        <html>
        <body>
            <h2>Thank you for your order!</h2>
            <p>Your order has been received and is being processed.</p>
            
            <h3>Order Details</h3>
            <p><strong>Order Number:</strong> {order.order_number}</p>
            <p><strong>Order Date:</strong> {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>Items</h3>
            <ul>
        """
        
        for item in items:
            html_body += f"<li>{products[item.id]} x {item.quantity} - ${item.price_cad * item.quantity:.2f} CAD</li>"
        
        html_body += f"""
            </ul>
            
            <p><strong>Subtotal:</strong> ${order.subtotal_cad:.2f} CAD</p>
            <p><strong>Shipping:</strong> ${order.shipping_cost_cad:.2f} CAD</p>
            <p><strong>Total:</strong> ${order.total_cad:.2f} CAD</p>
            
            <h3>Shipping Address</h3>
            <p>
                {order.customer_name}<br>
                {order.shipping_address_line1}<br>
                {order.shipping_address_line2 if order.shipping_address_line2 else ''}
                {order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}<br>
                {order.shipping_country}
            </p>
            
            <p>We will send you another email when your order ships.</p>
        </body>
        </html>
        """
        
        return self._send_email(order.customer_email, subject, html_body)
    
    async def send_payment_confirmation(self, order: Order, db: Session) -> bool:
        """Send payment confirmation email to customer."""
        subject = f"Payment Confirmed - {order.order_number}"
        
        html_body = f"""
        <html>
        <body>
            <h2>Payment Confirmed!</h2>
            <p>Your payment for order {order.order_number} has been confirmed.</p>
            <p>We are now processing your order and will ship it soon.</p>
            <p><strong>Total Paid:</strong> ${order.total_cad:.2f} CAD</p>
        </body>
        </html>
        """
        
        return self._send_email(order.customer_email, subject, html_body)
    
    async def send_shipping_notification(self, order: Order) -> bool:
        """Send shipping notification email to customer."""
        subject = f"Your Order Has Shipped - {order.order_number}"
        
        html_body = f"""
        <html>
        <body>
            <h2>Your order has shipped!</h2>
            <p>Order {order.order_number} has been shipped.</p>
            <p><strong>Tracking Number:</strong> {order.tracking_number}</p>
            <p>You can track your package using the tracking number above.</p>
        </body>
        </html>
        """
        
        return self._send_email(order.customer_email, subject, html_body)
    
    async def send_admin_notification(self, order: Order, db: Session) -> bool:
        """Send new order notification to admin."""
        if not settings.ADMIN_EMAIL:
            return False
        
        # Get order items
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        products = {}
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            products[item.id] = product.name if product else "Unknown"
        
        subject = f"New Order Received - {order.order_number}"
        
        html_body = f"""
        <html>
        <body>
            <h2>New Order Received</h2>
            <p><strong>Order Number:</strong> {order.order_number}</p>
            <p><strong>Customer:</strong> {order.customer_name} ({order.customer_email})</p>
            <p><strong>Total:</strong> ${order.total_cad:.2f} CAD</p>
            <p><strong>Payment Method:</strong> {order.payment_method}</p>
        </body>
        </html>
        """
        
        return self._send_email(settings.ADMIN_EMAIL, subject, html_body)





