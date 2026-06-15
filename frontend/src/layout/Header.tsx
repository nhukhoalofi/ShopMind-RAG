import { Badge } from "../components/common/Badge";

export function Header() {
  return (
    <header className="border-b border-slate-200 bg-white px-6 py-5 lg:px-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-950">ShopMind RAG</h1>
          <p className="text-sm text-slate-500">
            AI Customer Support Assistant for E-commerce
          </p>
        </div>
        <Badge tone="blue">FastAPI + Qdrant + Groq</Badge>
      </div>
    </header>
  );
}
