export interface ProductItem {
  product_id?: string | null;
  name?: string | null;
  category?: string | null;
  brand?: string | null;
  price?: number | null;
  stock?: number | null;
  description?: string | null;
  warranty?: string | null;
  avg_discount_rate?: number | null;
  transaction_count?: number | null;
  total_units_sold?: number | null;
  regions?: string[];
  source?: string | null;
}

export interface ProductSearchResponse {
  items: ProductItem[];
  count: number;
}
