import { Inbox } from "lucide-react";

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center text-slate-500">
      <Inbox className="mb-3 h-8 w-8" />
      <p>{message}</p>
    </div>
  );
}
