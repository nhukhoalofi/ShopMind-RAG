import type { ProductItem } from "../../types/product";
import { formatPrice, optionalText } from "../../utils/format";
import { Card } from "../common/Card";

export function ProductDetailCard({ product }: { product: ProductItem }) {
  return (
    <Card>
      <div className="flex flex-wrap justify-between gap-3">
        <div>
          <p className="font-mono text-xs text-slate-400">
            {optionalText(product.product_id)}
          </p>
          <h3 className="mt-1 text-xl font-bold text-slate-950">
            {optionalText(product.name)}
          </h3>
        </div>
        <p className="text-xl font-bold text-indigo-700">
          {formatPrice(product.price)}
        </p>
      </div>
      <dl className="mt-5 grid gap-4 text-sm sm:grid-cols-2">
        <div><dt className="font-semibold text-slate-500">Category</dt><dd>{optionalText(product.category)}</dd></div>
        <div><dt className="font-semibold text-slate-500">Brand</dt><dd>{optionalText(product.brand)}</dd></div>
        <div><dt className="font-semibold text-slate-500">Stock</dt><dd>{product.stock ?? "Not available"}</dd></div>
        <div><dt className="font-semibold text-slate-500">Warranty</dt><dd>{optionalText(product.warranty)}</dd></div>
        <div className="sm:col-span-2"><dt className="font-semibold text-slate-500">Description</dt><dd>{optionalText(product.description)}</dd></div>
      </dl>
    </Card>
  );
}
