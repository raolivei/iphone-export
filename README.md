# iPhone Export Ecommerce

**Ecommerce platform for selling iPhones with international shipping from Canada to Brazil.**

A modern, full-stack ecommerce website built for selling iPhones with support for Stripe and PayPal payments, inventory management, and admin panel.

## Overview

This platform enables selling iPhones with:

- Product catalog with detailed specifications
- Shopping cart and checkout flow
- Multiple payment options (Stripe and PayPal)
- Admin panel for managing products and orders
- Inventory tracking with stock management
- Email notifications for orders
- International shipping support (Canada to Brazil)

## Features

- 🛍️ **Product Catalog** - Browse iPhone models with detailed specifications
- 🛒 **Shopping Cart** - Add items, manage quantities, and proceed to checkout
- 💳 **Payment Processing** - Stripe and PayPal integration
- 📦 **Order Management** - Track orders from placement to delivery
- 👨‍💼 **Admin Panel** - Manage products, orders, and inventory
- 📊 **Inventory Tracking** - Real-time stock levels with low stock alerts
- 📧 **Email Notifications** - Order confirmations and status updates
- 🌍 **International Shipping** - Canada to Brazil shipping support

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11+, SQLAlchemy
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Payments**: Stripe, PayPal
- **Deployment**: Docker, Kubernetes (k3s)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)

### Docker Compose (Recommended)

```bash
# Load port assignments from workspace-config
source ../workspace-config/ports/.env.ports

# Start all services
docker-compose up -d

# Initialize database with seed data
docker-compose exec api python backend/init_db.py

# Access application
open http://localhost:3004
```

**Services:**

- Frontend: http://localhost:3004
- API: http://localhost:8004
- API Docs: http://localhost:8004/docs

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.server:app --reload --port 8004

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Project Structure

```
iphone-export/
├── backend/
│   ├── api/routes/      # API endpoints
│   ├── models/          # Pydantic models
│   ├── db/              # SQLAlchemy models
│   ├── services/        # Business logic (payment, email, inventory)
│   └── app/             # FastAPI configuration
├── frontend/
│   ├── pages/           # Next.js pages
│   ├── components/      # React components
│   └── styles/          # Tailwind CSS
├── k8s/                 # Kubernetes manifests
├── .github/workflows/   # CI/CD workflows
└── docker-compose.yml   # Local development
```

## Configuration

### Environment Variables

See `.env.example` for required environment variables:

- Database connection
- Redis connection
- Stripe API keys
- PayPal API keys
- Email service configuration
- Admin credentials

## Admin Access

Default admin credentials (change in production):

- Username: `admin`
- Password: Set via `ADMIN_PASSWORD` environment variable

## Deployment

### Docker Images

Images are published to GitHub Container Registry:

- `ghcr.io/raolivei/iphone-export-api:latest`
- `ghcr.io/raolivei/iphone-export-frontend:latest`

### Kubernetes

Deploy to k3s cluster:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
```

See `k8s/README.md` for detailed deployment instructions.

## Documentation

- [CHANGELOG.md](./CHANGELOG.md) - Version history
- [k8s/README.md](./k8s/README.md) - Deployment guide

## License

MIT




