export interface RagStatusResponse {
  qdrant_url: string;
  collection: string;
  collection_exists: boolean;
  embedding_model: string;
  top_k: number;
  min_score: number;
  max_score_gap: number;
}

export interface RetrievalSearchRequest {
  query: string;
  top_k: number;
}

export interface RetrievalResult {
  rank: number;
  score: number;
  chunk_id?: string | null;
  document_id?: string | null;
  document_type?: string | null;
  category?: string | null;
  source?: string | null;
  title?: string | null;
  text_preview?: string | null;
}

export interface RetrievalSearchResponse {
  query: string;
  results: RetrievalResult[];
}
