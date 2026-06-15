import type { EvaluationResult } from "../../types/evaluation";
import { formatScore } from "../../utils/format";
import { Badge } from "../common/Badge";

export function EvaluationResultTable({
  results,
}: {
  results: EvaluationResult[];
}) {
  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-left text-xs uppercase tracking-wider text-slate-500">
          <tr>
            <th className="px-4 py-3">Query</th>
            <th className="px-4 py-3">Answer</th>
            <th className="px-4 py-3">Score</th>
            <th className="px-4 py-3">Fallback</th>
            <th className="px-4 py-3">Sources</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {results.map((result) => (
            <tr key={result.query} className="align-top">
              <td className="max-w-xs px-4 py-3 font-medium text-slate-900">{result.query}</td>
              <td className="min-w-80 px-4 py-3 leading-6 text-slate-600">{result.answer}</td>
              <td className="px-4 py-3 font-semibold">{formatScore(result.best_score)}</td>
              <td className="px-4 py-3">
                <Badge tone={result.fallback ? "amber" : "emerald"}>
                  {result.fallback ? "Yes" : "No"}
                </Badge>
              </td>
              <td className="px-4 py-3">{result.sources.length}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
