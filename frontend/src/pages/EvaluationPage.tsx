import { FlaskConical } from "lucide-react";
import { useMemo, useState } from "react";

import { getApiErrorMessage } from "../api/httpClient";
import { runQuickEvaluation } from "../api/shopmindApi";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { MetricCard } from "../components/common/MetricCard";
import { EvaluationResultTable } from "../components/evaluation/EvaluationResultTable";
import type { EvaluationResult } from "../types/evaluation";

const defaults = `How long does shipping take?
What payment methods are accepted?
Can I cancel my order?
What happens if I receive a damaged product?
Do you offer warranty for products?
I forgot my account password. What should I do?
Do you have a physical store in Japan?`;

export function EvaluationPage() {
  const [queryText, setQueryText] = useState(defaults);
  const [results, setResults] = useState<EvaluationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const summary = useMemo(() => {
    const fallbackCount = results.filter((result) => result.fallback).length;
    const average = results.length ? results.reduce((sum, result) => sum + result.best_score, 0) / results.length : 0;
    return { fallbackCount, average };
  }, [results]);

  async function runEvaluation() {
    const queries = queryText.split("\n").map((query) => query.trim()).filter(Boolean);
    if (!queries.length) return;
    setLoading(true); setError("");
    try {
      setResults((await runQuickEvaluation({ queries })).results);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div><h2 className="text-2xl font-bold text-slate-950">RAG Evaluation Quick Test</h2><p className="text-slate-500">Run a compact batch evaluation through the complete pipeline.</p></div>
      <textarea className="input min-h-56 w-full" value={queryText} onChange={(event) => setQueryText(event.target.value)} />
      <Button onClick={runEvaluation} disabled={loading}><FlaskConical className="h-4 w-4" /> Run quick evaluation</Button>
      {error && <ErrorMessage message={error} />}
      {loading && <LoadingSpinner label="Running evaluation queries..." />}
      {results.length ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard label="Total queries" value={results.length} />
            <MetricCard label="Fallback count" value={summary.fallbackCount} />
            <MetricCard label="Fallback rate" value={`${((summary.fallbackCount / results.length) * 100).toFixed(1)}%`} />
            <MetricCard label="Average best score" value={summary.average.toFixed(4)} />
          </div>
          <EvaluationResultTable results={results} />
        </>
      ) : !loading && <EmptyState message="Run the default questions or provide your own batch." />}
    </div>
  );
}
