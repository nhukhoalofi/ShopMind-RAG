import { Search } from "lucide-react";
import { useState } from "react";

import { getApiErrorMessage } from "../api/httpClient";
import { getProductDetail, searchProducts } from "../api/shopmindApi";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ProductDetailCard } from "../components/products/ProductDetailCard";
import { ProductTable } from "../components/products/ProductTable";
import type { ProductItem } from "../types/product";

export function ProductsPage() {
  const [filters, setFilters] = useState({ q: "", category: "", brand: "", min: "", max: "", limit: 20 });
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [productId, setProductId] = useState("");
  const [detail, setDetail] = useState<ProductItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function search() {
    setLoading(true);
    setError("");
    try {
      const response = await searchProducts({
        q: filters.q || undefined,
        category: filters.category || undefined,
        brand: filters.brand || undefined,
        min_price: filters.min ? Number(filters.min) : undefined,
        max_price: filters.max ? Number(filters.max) : undefined,
        limit: filters.limit,
      });
      setProducts(response.items);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  async function loadDetail() {
    if (!productId.trim()) return;
    setError("");
    try {
      setDetail(await getProductDetail(productId.trim()));
    } catch (requestError) {
      setDetail(null);
      setError(getApiErrorMessage(requestError));
    }
  }

  return (
    <div className="space-y-6">
      <div><h2 className="text-2xl font-bold text-slate-950">Product Search</h2><p className="text-slate-500">Search structured product records from the backend.</p></div>
      <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-5 md:grid-cols-3">
        {(["q", "category", "brand"] as const).map((key) => (
          <input key={key} className="input" placeholder={key === "q" ? "Name or product ID" : key[0].toUpperCase() + key.slice(1)} value={filters[key]} onChange={(event) => setFilters({ ...filters, [key]: event.target.value })} />
        ))}
        <input className="input" type="number" min="0" placeholder="Minimum price" value={filters.min} onChange={(event) => setFilters({ ...filters, min: event.target.value })} />
        <input className="input" type="number" min="0" placeholder="Maximum price" value={filters.max} onChange={(event) => setFilters({ ...filters, max: event.target.value })} />
        <select className="input" value={filters.limit} onChange={(event) => setFilters({ ...filters, limit: Number(event.target.value) })}>
          {[10, 20, 50, 100].map((value) => <option key={value} value={value}>Limit {value}</option>)}
        </select>
        <Button onClick={search} disabled={loading}><Search className="h-4 w-4" /> Search products</Button>
      </div>
      {error && <ErrorMessage message={error} />}
      {loading ? <LoadingSpinner label="Loading products..." /> : products.length ? <ProductTable products={products} /> : <EmptyState message="Search to browse available products." />}
      <div className="grid gap-5 lg:grid-cols-[360px_1fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <h3 className="font-semibold text-slate-900">Product detail lookup</h3>
          <input className="input mt-4" placeholder="Product_1" value={productId} onChange={(event) => setProductId(event.target.value)} />
          <Button className="mt-3 w-full" onClick={loadDetail} disabled={!productId.trim()}>Get detail</Button>
        </div>
        {detail ? <ProductDetailCard product={detail} /> : <EmptyState message="Enter a product ID to view details." />}
      </div>
    </div>
  );
}
