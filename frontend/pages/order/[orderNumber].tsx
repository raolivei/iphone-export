import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { ordersApi, Order } from '@/utils/api';

export default function OrderConfirmation() {
  const router = useRouter();
  const { orderNumber } = router.query;
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (orderNumber) {
      const fetchOrder = async () => {
        try {
          const data = await ordersApi.get(orderNumber as string);
          setOrder(data);
        } catch {
          // Silently handle error
        } finally {
          setLoading(false);
        }
      };
      fetchOrder();
    }
  }, [orderNumber]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Order not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link href="/" className="text-2xl font-bold text-gray-900">
            iPhone Export
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">✓</div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Order Confirmed!
            </h1>
            <p className="text-gray-600">
              Thank you for your order. We've sent a confirmation email to {order.customer_email}
            </p>
          </div>

          <div className="border-t border-b py-6 mb-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-600">Order Number</p>
                <p className="text-lg font-semibold">{order.order_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="text-lg font-semibold capitalize">{order.status}</p>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-4">Order Details</h2>
            <div className="space-y-2">
              {order.items.map((item) => (
                <div key={item.id} className="flex justify-between">
                  <span className="text-gray-700">
                    {item.product_name} x {item.quantity}
                  </span>
                  <span className="font-semibold">${item.subtotal_cad.toFixed(2)} CAD</span>
                </div>
              ))}
            </div>
            <div className="border-t mt-4 pt-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-semibold">${order.subtotal_cad.toFixed(2)} CAD</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Shipping</span>
                <span className="font-semibold">${order.shipping_cost_cad.toFixed(2)} CAD</span>
              </div>
              <div className="flex justify-between text-lg font-bold">
                <span>Total</span>
                <span>${order.total_cad.toFixed(2)} CAD</span>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-4">Shipping Address</h2>
            <p className="text-gray-700">
              {order.customer_name}<br />
              {order.shipping_address_line1}<br />
              {order.shipping_address_line2 && `${order.shipping_address_line2}<br />`}
              {order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}<br />
              {order.shipping_country}
            </p>
          </div>

          {order.tracking_number && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Tracking Number</h2>
              <p className="text-gray-700">{order.tracking_number}</p>
            </div>
          )}

          <Link
            href="/"
            className="block text-center bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 text-lg font-semibold"
          >
            Continue Shopping
          </Link>
        </div>
      </main>
    </div>
  );
}





