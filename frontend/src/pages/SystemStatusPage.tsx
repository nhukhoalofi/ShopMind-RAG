import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

import { getApiErrorMessage } from "../api/httpClient";
import { getHealth, getRagStatus } from "../api/shopmindApi";
import { Badge } from "../components/common/Badge";
import { Button } from "../components/common/Button";
import { Card } from "../components/common/Card";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { MetricCard } from "../components/common/MetricCard";
import type { RagStatusResponse } from "../types/rag";

export function SystemStatusPage() {
  const [health, setHealth] = useState<{ status: string; app: string } | null>(null);
  const [rag, setRag] = useState<RagStatusResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function refresh() {
    setLoading(true); setError("");
    try {
      const [healthResponse, ragResponse] = await Promise.all([getHealth(), getRagStatus()]);
      setHealth(healthResponse); setRag(ragResponse);
    } catch (requestError) {
      setHealth(null); setRag(null); setError(getApiErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void refresh(); }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-3">
        <div><h2 className="text-2xl font-bold text-slate-950">System Status</h2><p className="text-slate-500">FastAPI, Qdrant, and retrieval configuration.</p></div>
        <Button onClick={refresh} disabled={loading}><RefreshCw className="h-4 w-4" /> Refresh</Button>
      </div>
      {error && <ErrorMessage message={error} />}
      {loading && <LoadingSpinner label="Checking backend services..." />}
      {health && rag && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard label="Backend status" value={health.status} hint={health.app} />
            <MetricCard label="Collection" value={rag.collection} />
            <MetricCard label="Top K" value={rag.top_k} />
            <MetricCard label="Minimum score" value={rag.min_score} />
          </div>
          <Card>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h3 className="text-lg font-semibold">RAG configuration</h3>
              <Badge tone={rag.collection_exists ? "emerald" : "rose"}>
                Collection {rag.collection_exists ? "available" : "missing"}
              </Badge>
            </div>
            <dl className="mt-5 grid gap-4 text-sm sm:grid-cols-2">
              <div><dt className="font-semibold text-slate-500">Qdrant URL</dt><dd>{rag.qdrant_url}</dd></div>
              <div><dt className="font-semibold text-slate-500">Embedding model</dt><dd>{rag.embedding_model}</dd></div>
              <div><dt className="font-semibold text-slate-500">Max score gap</dt><dd>{rag.max_score_gap}</dd></div>
              <div><dt className="font-semibold text-slate-500">Collection exists</dt><dd>{rag.collection_exists ? "Yes" : "No"}</dd></div>
            </dl>
          </Card>
        </>
      )}
    </div>
  );
}
