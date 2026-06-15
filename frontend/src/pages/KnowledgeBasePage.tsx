import { useEffect, useState } from "react";

import { getApiErrorMessage } from "../api/httpClient";
import { getCategories, getDocuments } from "../api/shopmindApi";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { MetricCard } from "../components/common/MetricCard";
import type { CategoryItem, DocumentItem } from "../types/document";
import { optionalText } from "../utils/format";

export function KnowledgeBasePage() {
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [filters, setFilters] = useState({ documentType: "", category: "", limit: 50 });
  const [error, setError] = useState("");

  useEffect(() => {
    getCategories().then((response) => setCategories(response.categories)).catch((requestError) => setError(getApiErrorMessage(requestError)));
  }, []);

  async function loadDocuments() {
    setError("");
    try {
      const response = await getDocuments({
        document_type: filters.documentType || undefined,
        category: filters.category || undefined,
        limit: filters.limit,
      });
      setDocuments(response.items);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    }
  }

  return (
    <div className="space-y-6">
      <div><h2 className="text-2xl font-bold text-slate-950">Knowledge Base</h2><p className="text-slate-500">Browse categories and documents used for grounded answers.</p></div>
      {error && <ErrorMessage message={error} />}
      <div className="grid gap-4 sm:grid-cols-2">
        <MetricCard label="Total categories" value={categories.length} />
        <MetricCard label="Displayed documents" value={documents.length} />
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {categories.map((category) => (
          <button key={category.name} type="button" onClick={() => setFilters({ ...filters, category: category.name })} className="rounded-2xl border border-slate-200 bg-white p-4 text-left hover:border-indigo-300">
            <p className="font-semibold text-slate-900">{category.name}</p>
            <p className="text-sm text-slate-500">{category.document_count} documents</p>
          </button>
        ))}
      </div>
      <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-5 md:grid-cols-[1fr_1fr_160px_auto]">
        <select className="input" value={filters.documentType} onChange={(event) => setFilters({ ...filters, documentType: event.target.value })}>
          <option value="">All document types</option><option value="faq">FAQ</option><option value="policy">Policy</option><option value="product">Product</option>
        </select>
        <select className="input" value={filters.category} onChange={(event) => setFilters({ ...filters, category: event.target.value })}>
          <option value="">All categories</option>{categories.map((category) => <option key={category.name} value={category.name}>{category.name}</option>)}
        </select>
        <select className="input" value={filters.limit} onChange={(event) => setFilters({ ...filters, limit: Number(event.target.value) })}>
          {[20, 50, 100, 200].map((value) => <option key={value} value={value}>Limit {value}</option>)}
        </select>
        <Button onClick={loadDocuments}>Load documents</Button>
      </div>
      {documents.length ? (
        <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500"><tr>{["Document ID", "Type", "Category", "Source", "Title"].map((label) => <th key={label} className="px-4 py-3">{label}</th>)}</tr></thead>
            <tbody className="divide-y divide-slate-100">{documents.map((document, index) => <tr key={document.document_id ?? index}><td className="px-4 py-3 font-mono text-xs">{optionalText(document.document_id)}</td><td className="px-4 py-3">{optionalText(document.document_type)}</td><td className="px-4 py-3">{optionalText(document.category)}</td><td className="px-4 py-3">{optionalText(document.source)}</td><td className="px-4 py-3 font-medium">{optionalText(document.title)}</td></tr>)}</tbody>
          </table>
        </div>
      ) : <EmptyState message="Load documents using the filters above." />}
    </div>
  );
}
