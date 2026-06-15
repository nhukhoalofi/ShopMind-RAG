import { httpClient } from "./httpClient";
import type { ChatRequest, ChatResponse } from "../types/chat";
import type {
  CategoriesResponse,
  DocumentsResponse,
} from "../types/document";
import type {
  EvaluationRequest,
  EvaluationResponse,
} from "../types/evaluation";
import type {
  ProductItem,
  ProductSearchResponse,
} from "../types/product";
import type {
  RagStatusResponse,
  RetrievalSearchRequest,
  RetrievalSearchResponse,
} from "../types/rag";

export async function getHealth(): Promise<{
  status: string;
  app: string;
}> {
  const { data } = await httpClient.get("/health");
  return data;
}

export async function getRagStatus(): Promise<RagStatusResponse> {
  const { data } = await httpClient.get("/api/v1/rag/status");
  return data;
}

export async function sendChatMessage(
  payload: ChatRequest,
): Promise<ChatResponse> {
  const { data } = await httpClient.post("/api/v1/chat", payload, {
    timeout: 120000,
  });
  return data;
}

export async function searchRetrieval(
  payload: RetrievalSearchRequest,
): Promise<RetrievalSearchResponse> {
  const { data } = await httpClient.post(
    "/api/v1/retrieval/search",
    payload,
  );
  return data;
}

export async function getDocuments(params: {
  document_type?: string;
  category?: string;
  limit?: number;
}): Promise<DocumentsResponse> {
  const { data } = await httpClient.get("/api/v1/documents", { params });
  return data;
}

export async function getCategories(): Promise<CategoriesResponse> {
  const { data } = await httpClient.get("/api/v1/categories");
  return data;
}

export async function searchProducts(params: {
  q?: string;
  category?: string;
  brand?: string;
  min_price?: number;
  max_price?: number;
  limit?: number;
}): Promise<ProductSearchResponse> {
  const { data } = await httpClient.get("/api/v1/products/search", {
    params,
  });
  return data;
}

export async function getProductDetail(
  productId: string,
): Promise<ProductItem> {
  const { data } = await httpClient.get(
    `/api/v1/products/${encodeURIComponent(productId)}`,
  );
  return data;
}

export async function runQuickEvaluation(
  payload: EvaluationRequest,
): Promise<EvaluationResponse> {
  const { data } = await httpClient.post(
    "/api/v1/evaluation/quick-test",
    payload,
    { timeout: 180000 },
  );
  return data;
}
