import type { SourceItem } from "../../types/chat";
import { formatScore, optionalText } from "../../utils/format";
import { Badge } from "../common/Badge";
import { Card } from "../common/Card";

export function SourceCard({ source }: { source: SourceItem }) {
  return (
    <Card className="bg-slate-50 p-4 shadow-none">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <p className="font-semibold text-slate-900">
          {optionalText(source.title)}
        </p>
        <Badge tone="blue">Score {formatScore(source.score)}</Badge>
      </div>
      <dl className="grid gap-2 text-xs text-slate-600 sm:grid-cols-2">
        <div><dt className="font-semibold">Rank</dt><dd>{source.rank}</dd></div>
        <div><dt className="font-semibold">Type</dt><dd>{optionalText(source.document_type)}</dd></div>
        <div><dt className="font-semibold">Category</dt><dd>{optionalText(source.category)}</dd></div>
        <div><dt className="font-semibold">Source</dt><dd>{optionalText(source.source)}</dd></div>
        <div><dt className="font-semibold">Chunk ID</dt><dd className="break-all">{optionalText(source.chunk_id)}</dd></div>
        <div><dt className="font-semibold">Document ID</dt><dd className="break-all">{optionalText(source.document_id)}</dd></div>
      </dl>
    </Card>
  );
}
