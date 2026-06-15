from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.chat_routes import router as chat_router
from backend.app.api.v1.document_routes import (
    categories_router,
    router as document_router,
)
from backend.app.api.v1.evaluation_routes import router as evaluation_router
from backend.app.api.v1.product_routes import router as product_router
from backend.app.api.v1.rag_routes import router as rag_router
from backend.app.api.v1.retrieval_routes import router as retrieval_router
from backend.app.config import settings


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "Backend health checks."},
        {"name": "chat", "description": "RAG customer support chat."},
        {"name": "rag", "description": "RAG configuration and status."},
        {"name": "retrieval", "description": "Semantic retrieval debugging."},
        {"name": "documents", "description": "Knowledge base metadata."},
        {"name": "products", "description": "Structured product lookup."},
        {"name": "evaluation", "description": "RAG quick evaluation."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(rag_router, prefix="/api/v1/rag", tags=["rag"])
app.include_router(
    retrieval_router,
    prefix="/api/v1/retrieval",
    tags=["retrieval"],
)
app.include_router(
    document_router,
    prefix="/api/v1/documents",
    tags=["documents"],
)
app.include_router(categories_router, prefix="/api/v1", tags=["documents"])
app.include_router(
    product_router,
    prefix="/api/v1/products",
    tags=["products"],
)
app.include_router(
    evaluation_router,
    prefix="/api/v1/evaluation",
    tags=["evaluation"],
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
