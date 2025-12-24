import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { productsApi, Product } from '@/utils/api';
import { useCartStore } from '@/store/cartStore';

export default function ProductDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const { addItem } = useCartStore();

  useEffect(() => {
    if (id) {
      const fetchProduct = async () => {
        try {
          const data = await productsApi.get(Number(id));
          setProduct(data);
        } catch (error) {
          console.error('Failed to fetch product:', error);
        } finally {
          setLoading(false);
        }
      };
      fetchProduct();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Product not found</div>
      </div>
    );
  }

  const handleAddToCart = () => {
    for (let i = 0; i < quantity; i++) {
      addItem(product);
    }
    router.push('/cart');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <Link href="/" className="text-2xl font-bold text-gray-900">
              iPhone Export
            </Link>
            <Link
              href="/cart"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Cart
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-8">
            <div>
              {product.image_url && (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full rounded-lg"
                />
              )}
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                {product.name}
              </h1>
              <p className="text-2xl font-bold text-gray-900 mb-4">
                ${product.price_cad.toFixed(2)} CAD
              </p>
              <p className="text-gray-600 mb-6">{product.description}</p>
              
              {product.specifications && (
                <div className="mb-6">
                  <h2 className="text-xl font-semibold mb-2">Specifications</h2>
                  <p className="text-gray-700 whitespace-pre-line">
                    {product.specifications}
                  </p>
                </div>
              )}

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quantity
                </label>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="bg-gray-200 px-4 py-2 rounded-lg hover:bg-gray-300"
                  >
                    -
                  </button>
                  <span className="text-xl font-semibold">{quantity}</span>
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    className="bg-gray-200 px-4 py-2 rounded-lg hover:bg-gray-300"
                  >
                    +
                  </button>
                </div>
              </div>

              {product.is_in_stock ? (
                <button
                  onClick={handleAddToCart}
                  className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 text-lg font-semibold"
                >
                  Add to Cart
                </button>
              ) : (
                <div className="w-full bg-gray-300 text-gray-600 px-6 py-3 rounded-lg text-center text-lg font-semibold">
                  Out of Stock
                </div>
              )}

              {product.is_low_stock && product.is_in_stock && (
                <p className="text-orange-600 text-sm mt-2">Low stock - only {product.stock_quantity} left!</p>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}





