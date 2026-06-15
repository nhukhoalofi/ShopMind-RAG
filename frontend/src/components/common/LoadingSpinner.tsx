import { LoaderCircle } from "lucide-react";

export function LoadingSpinner({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-500">
      <LoaderCircle className="h-4 w-4 animate-spin" />
      {label}
    </div>
  );
}
