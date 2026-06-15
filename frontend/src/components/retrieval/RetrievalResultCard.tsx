import type { RetrievalResult } from "../../types/rag";
import { formatScore, optionalText } from "../../utils/format";
import { Badge } from "../common/Badge";
import { Card } from "../common/Card";

export function RetrievalResultCard({
  result,
}: {
  result: RetrievalResult;
}) {
  return (
    <Card>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-indigo-600">
            Result #{result.rank}
          </p>
          <h3 className="mt-1 font-semibold text-slate-950">
            {optionalText(result.title)}
          </h3>
        </div>
        <span className="rounded-xl bg-indigo-600 px-3 py-2 text-lg font-bold text-white">
          {formatScore(result.score)}
        </span>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Badge tone="blue">{optionalText(result.document_type)}</Badge>
        <Badge tone="emerald">{optionalText(result.category)}</Badge>
        <Badge>{optionalText(result.source)}</Badge>
      </div>
      <details className="mt-4 rounded-xl bg-slate-50 p-3">
        <summary className="cursor-pointer text-sm font-semibold text-slate-700">
          Text preview
        </summary>
        <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-600">
          {optionalText(result.text_preview)}
        </p>
      </details>
    </Card>
  );
}
