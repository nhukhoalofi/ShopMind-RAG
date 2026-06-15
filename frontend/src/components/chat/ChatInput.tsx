import { Send } from "lucide-react";
import { useState } from "react";

import { Button } from "../common/Button";

export function ChatInput({
  onSubmit,
  disabled,
}: {
  onSubmit: (message: string) => void;
  disabled?: boolean;
}) {
  const [message, setMessage] = useState("");

  function submit() {
    const cleaned = message.trim();
    if (!cleaned || disabled) return;
    onSubmit(cleaned);
    setMessage("");
  }

  return (
    <div className="flex gap-3 border-t border-slate-200 bg-white p-4">
      <input
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submit();
          }
        }}
        placeholder="Ask a customer support question..."
        className="min-w-0 flex-1 rounded-xl border border-slate-300 px-4 py-3 outline-none ring-indigo-200 focus:border-indigo-500 focus:ring-4"
        disabled={disabled}
      />
      <Button onClick={submit} disabled={disabled || !message.trim()}>
        <Send className="h-4 w-4" />
        Send
      </Button>
    </div>
  );
}
