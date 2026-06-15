import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./layout/AppLayout";
import { ChatPage } from "./pages/ChatPage";
import { EvaluationPage } from "./pages/EvaluationPage";
import { KnowledgeBasePage } from "./pages/KnowledgeBasePage";
import { ProductsPage } from "./pages/ProductsPage";
import { RetrievalDebugPage } from "./pages/RetrievalDebugPage";
import { SystemStatusPage } from "./pages/SystemStatusPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/chat" replace />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/retrieval" element={<RetrievalDebugPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
        <Route path="/evaluation" element={<EvaluationPage />} />
        <Route path="/status" element={<SystemStatusPage />} />
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Route>
    </Routes>
  );
}
