import { Search } from "lucide-react";
import { useState } from "react";

import { getApiErrorMessage } from "../api/httpClient";
import { searchRetrieval } from "../api/shopmindApi";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { RetrievalResultCard } from "../components/retrieval/RetrievalResultCard";
import type { RetrievalResult } from "../types/rag";

export function RetrievalDebugPage() {
  const [query, setQuery] = useState("What payment methods are accepted?");
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState<RetrievalResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runSearch() {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const response = await searchRetrieval({ query: query.trim(), top_k: topK });
      setResults(response.results);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-2xl font-bold text-slate-950">Retrieval Debug</h2>
        <p className="text-slate-500">Inspect semantic search without calling the LLM.</p>
      </div>
      <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-5 md:grid-cols-[1fr_140px_auto]">
        <input className="input" value={query} onChange={(event) => setQuery(event.target.value)} />
        <select className="input" value={topK} onChange={(event) => setTopK(Number(event.target.value))}>
          {Array.from({ length: 10 }, (_, index) => index + 1).map((value) => (
            <option key={value} value={value}>Top {value}</option>
          ))}
        </select>
        <Button onClick={runSearch} disabled={loading || !query.trim()}>
          <Search className="h-4 w-4" /> Run retrieval
        </Button>
      </div>
      {error && <ErrorMessage message={error} />}
      {loading && <LoadingSpinner label="Searching vector index..." />}
      {!loading && results.length === 0 ? (
        <EmptyState message="Run a query to inspect retrieved chunks." />
      ) : (
        <div className="grid gap-4 xl:grid-cols-2">
          {results.map((result) => (
            <RetrievalResultCard key={`${result.rank}-${result.chunk_id}`} result={result} />
          ))}
        </div>
      )}
    </div>
  );
}
