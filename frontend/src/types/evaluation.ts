import type { SourceItem } from "./chat";

export interface EvaluationRequest {
  queries: string[];
}

export interface EvaluationResult {
  query: string;
  answer: string;
  best_score: number;
  fallback: boolean;
  sources: SourceItem[];
}

export interface EvaluationResponse {
  results: EvaluationResult[];
}
