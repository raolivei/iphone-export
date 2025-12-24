import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Product {
  id: number;
  name: string;
  description: string | null;
  price_cad: number;
  image_url: string | null;
  specifications: string | null;
  is_active: boolean;
  stock_quantity: number | null;
  is_in_stock: boolean | null;
  is_low_stock: boolean | null;
}

export interface CartItem {
  product_id: number;
  quantity: number;
}

export interface ShippingAddress {
  name: string;
  email: string;
  phone?: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

export interface CheckoutRequest {
  items: CartItem[];
  shipping_address: ShippingAddress;
  payment_method: 'stripe' | 'paypal';
}

export interface Order {
  id: number;
  order_number: string;
  status: string;
  payment_method: string | null;
  customer_name: string;
  customer_email: string;
  customer_phone: string | null;
  shipping_address_line1: string;
  shipping_address_line2: string | null;
  shipping_city: string;
  shipping_state: string;
  shipping_postal_code: string;
  shipping_country: string;
  subtotal_cad: number;
  shipping_cost_cad: number;
  total_cad: number;
  tracking_number: string | null;
  items: Array<{
    id: number;
    product_id: number;
    product_name: string;
    quantity: number;
    price_cad: number;
    subtotal_cad: number;
  }>;
  created_at: string;
  updated_at: string | null;
  shipped_at: string | null;
  delivered_at: string | null;
}

export const productsApi = {
  list: async (): Promise<Product[]> => {
    const response = await api.get('/api/products/');
    return response.data.products;
  },
  get: async (id: number): Promise<Product> => {
    const response = await api.get(`/api/products/${id}`);
    return response.data;
  },
};

export const checkoutApi = {
  create: async (data: CheckoutRequest): Promise<Order> => {
    const response = await api.post('/api/checkout/', data);
    return response.data;
  },
};

export const ordersApi = {
  get: async (orderNumber: string): Promise<Order> => {
    const response = await api.get(`/api/orders/by-number/${orderNumber}`);
    return response.data;
  },
};

export default api;





