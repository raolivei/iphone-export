import { useEffect, useState } from 'react';
import Link from 'next/link';
import { productsApi, Product } from '@/utils/api';
import { useCartStore } from '@/store/cartStore';

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const { addItem } = useCartStore();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const data = await productsApi.list();
        setProducts(data);
      } catch {
        // Silently handle error
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">iPhone Export</h1>
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
        <h2 className="text-3xl font-bold text-gray-900 mb-8">Our Products</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <div
              key={product.id}
              className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
            >
              {product.image_url && (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full h-64 object-cover"
                />
              )}
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {product.name}
                </h3>
                <p className="text-gray-600 mb-4 line-clamp-2">
                  {product.description}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-gray-900">
                    ${product.price_cad.toFixed(2)} CAD
                  </span>
                  {product.is_in_stock ? (
                    <button
                      onClick={() => addItem(product)}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                    >
                      Add to Cart
                    </button>
                  ) : (
                    <span className="text-red-600 font-semibold">Out of Stock</span>
                  )}
                </div>
                {product.is_low_stock && product.is_in_stock && (
                  <p className="text-orange-600 text-sm mt-2">Low stock!</p>
                )}
                <Link
                  href={`/products/${product.id}`}
                  className="text-blue-600 hover:text-blue-800 mt-4 inline-block"
                >
                  View Details →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}





