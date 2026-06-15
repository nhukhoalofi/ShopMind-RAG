import { Bot, User } from "lucide-react";
import clsx from "clsx";

import type { ChatHistoryItem } from "../../types/chat";
import { formatScore } from "../../utils/format";
import { Badge } from "../common/Badge";
import { SourceCard } from "./SourceCard";

export function ChatMessage({ item }: { item: ChatHistoryItem }) {
  const assistant = item.role === "assistant";
  const sources = item.metadata?.sources ?? [];
  return (
    <div className={clsx("flex gap-3", !assistant && "justify-end")}>
      {assistant && (
        <div className="mt-1 rounded-xl bg-indigo-100 p-2 text-indigo-700">
          <Bot className="h-5 w-5" />
        </div>
      )}
      <div
        className={clsx(
          "max-w-3xl rounded-2xl px-4 py-3",
          assistant
            ? "border border-slate-200 bg-white text-slate-800"
            : "bg-indigo-600 text-white",
        )}
      >
        <p className="whitespace-pre-wrap leading-7">{item.content}</p>
        {assistant && item.metadata && (
          <div className="mt-4 space-y-3">
            <div className="flex flex-wrap gap-2">
              <Badge tone={item.metadata.fallback ? "amber" : "emerald"}>
                {item.metadata.fallback ? "Fallback" : "Grounded answer"}
              </Badge>
              <Badge tone="blue">
                Best score {formatScore(item.metadata.best_score)}
              </Badge>
            </div>
            {sources.length > 0 && (
              <details>
                <summary className="cursor-pointer text-sm font-semibold text-indigo-700">
                  View {sources.length} source{sources.length === 1 ? "" : "s"}
                </summary>
                <div className="mt-3 grid gap-3">
                  {sources.map((source) => (
                    <SourceCard
                      key={`${source.rank}-${source.chunk_id ?? source.title}`}
                      source={source}
                    />
                  ))}
                </div>
              </details>
            )}
          </div>
        )}
      </div>
      {!assistant && (
        <div className="mt-1 rounded-xl bg-slate-200 p-2 text-slate-700">
          <User className="h-5 w-5" />
        </div>
      )}
    </div>
  );
}
