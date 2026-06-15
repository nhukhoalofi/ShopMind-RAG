export interface SourceItem {
  rank: number;
  score: number;
  chunk_id?: string | null;
  document_id?: string | null;
  document_type?: string | null;
  category?: string | null;
  source?: string | null;
  title?: string | null;
}

export interface ChatRequest {
  message: string;
  session_id?: string | null;
}

export interface ChatResponse {
  answer: string;
  best_score: number;
  sources: SourceItem[];
  fallback: boolean;
}

export interface ChatHistoryItem {
  id: string;
  role: "user" | "assistant";
  content: string;
  metadata?: {
    best_score?: number;
    fallback?: boolean;
    sources?: SourceItem[];
  };
}
