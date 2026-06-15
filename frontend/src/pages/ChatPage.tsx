import { Trash2 } from "lucide-react";
import { useState } from "react";

import { sendChatMessage } from "../api/shopmindApi";
import { getApiErrorMessage } from "../api/httpClient";
import { ChatInput } from "../components/chat/ChatInput";
import { ChatMessage } from "../components/chat/ChatMessage";
import { ExampleQuestions } from "../components/chat/ExampleQuestions";
import { Button } from "../components/common/Button";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import type { ChatHistoryItem } from "../types/chat";

export function ChatPage() {
  const [history, setHistory] = useState<ChatHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(message: string) {
    const userItem: ChatHistoryItem = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
    };
    setHistory((current) => [...current, userItem]);
    setLoading(true);
    setError("");
    try {
      const response = await sendChatMessage({
        message,
        session_id: "react-session",
      });
      setHistory((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.answer,
          metadata: {
            best_score: response.best_score,
            fallback: response.fallback,
            sources: response.sources,
          },
        },
      ]);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-slate-950">Customer Support Chat</h2>
          <p className="text-slate-500">Answers grounded in the ShopMind knowledge base.</p>
        </div>
        <Button className="bg-slate-800 hover:bg-slate-900" onClick={() => setHistory([])}>
          <Trash2 className="h-4 w-4" /> Clear chat
        </Button>
      </div>
      <ExampleQuestions onSelect={submit} disabled={loading} />
      {error && <ErrorMessage message={error} />}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-slate-100">
        <div className="min-h-[440px] space-y-5 p-5">
          {history.length === 0 && (
            <div className="grid h-96 place-items-center text-center text-slate-500">
              <div>
                <p className="text-lg font-semibold text-slate-700">How can ShopMind help?</p>
                <p className="mt-1 text-sm">Choose an example or ask your own support question.</p>
              </div>
            </div>
          )}
          {history.map((item) => <ChatMessage key={item.id} item={item} />)}
          {loading && <LoadingSpinner label="Retrieving context and generating an answer..." />}
        </div>
        <ChatInput onSubmit={submit} disabled={loading} />
      </div>
    </div>
  );
}
