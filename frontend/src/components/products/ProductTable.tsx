import type { ProductItem } from "../../types/product";
import { formatPrice, optionalText } from "../../utils/format";

export function ProductTable({ products }: { products: ProductItem[] }) {
  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-left text-xs uppercase tracking-wider text-slate-500">
          <tr>
            {["Product ID", "Name", "Category", "Brand", "Price", "Stock"].map((label) => (
              <th key={label} className="px-4 py-3">{label}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {products.map((product, index) => (
            <tr key={product.product_id ?? index} className="hover:bg-slate-50">
              <td className="px-4 py-3 font-mono text-xs">{optionalText(product.product_id)}</td>
              <td className="px-4 py-3 font-medium text-slate-900">{optionalText(product.name)}</td>
              <td className="px-4 py-3">{optionalText(product.category)}</td>
              <td className="px-4 py-3">{optionalText(product.brand)}</td>
              <td className="px-4 py-3">{formatPrice(product.price)}</td>
              <td className="px-4 py-3">{product.stock ?? "Not available"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
