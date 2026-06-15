export interface DocumentItem {
  document_id?: string | null;
  document_type?: string | null;
  category?: string | null;
  source?: string | null;
  title?: string | null;
}

export interface DocumentsResponse {
  items: DocumentItem[];
  count: number;
}

export interface CategoryItem {
  name: string;
  document_count: number;
}

export interface CategoriesResponse {
  categories: CategoryItem[];
}
