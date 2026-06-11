# setup_project.ps1
# Create ShopMind RAG project structure
# If folders/files already exist, keep them unchanged.

# $ProjectRoot = "ShopMind RAG"

# # -----------------------------
# # 1. Create root folder
# # -----------------------------
# if (-not (Test-Path $ProjectRoot)) {
#     New-Item -ItemType Directory -Path $ProjectRoot | Out-Null
#     Write-Host "Created folder: $ProjectRoot"
# } else {
#     Write-Host "Folder already exists: $ProjectRoot"
# }

# Set-Location $ProjectRoot
Write-Host "Creating ShopMind RAG structure at: $(Get-Location)"
# -----------------------------
# 2. Folder list
# -----------------------------
$Folders = @(
    "backend/app/api/v1",
    "backend/app/schemas",
    "backend/app/models",
    "backend/app/repositories",
    "backend/app/services",
    "backend/app/rag",
    "backend/app/tools",
    "backend/app/db",
    "backend/app/utils",

    "frontend",

    "data/external",
    "data/raw",
    "data/processed",
    "data/evaluation",

    "scripts",

    "notebooks",

    "docs"
)

foreach ($Folder in $Folders) {
    if (-not (Test-Path $Folder)) {
        New-Item -ItemType Directory -Path $Folder -Force | Out-Null
        Write-Host "Created folder: $Folder"
    } else {
        Write-Host "Folder already exists: $Folder"
    }
}

# -----------------------------
# 3. File list
# -----------------------------
$Files = @(
    "README.md",
    "docker-compose.yml",
    ".env.example",
    "requirements.txt",

    "backend/app/main.py",
    "backend/app/config.py",

    "backend/app/api/v1/chat_routes.py",
    "backend/app/api/v1/document_routes.py",
    "backend/app/api/v1/product_routes.py",
    "backend/app/api/v1/order_routes.py",
    "backend/app/api/v1/evaluation_routes.py",

    "backend/app/schemas/chat_schema.py",
    "backend/app/schemas/document_schema.py",
    "backend/app/schemas/product_schema.py",
    "backend/app/schemas/order_schema.py",
    "backend/app/schemas/evaluation_schema.py",

    "backend/app/models/product.py",
    "backend/app/models/document.py",
    "backend/app/models/chunk.py",
    "backend/app/models/order.py",
    "backend/app/models/return_request.py",
    "backend/app/models/chat_log.py",

    "backend/app/repositories/product_repository.py",
    "backend/app/repositories/document_repository.py",
    "backend/app/repositories/order_repository.py",
    "backend/app/repositories/return_repository.py",
    "backend/app/repositories/chat_log_repository.py",

    "backend/app/services/chat_service.py",
    "backend/app/services/document_service.py",
    "backend/app/services/product_service.py",
    "backend/app/services/order_service.py",
    "backend/app/services/ingestion_service.py",
    "backend/app/services/evaluation_service.py",

    "backend/app/rag/chunker.py",
    "backend/app/rag/embedder.py",
    "backend/app/rag/vector_store.py",
    "backend/app/rag/retriever.py",
    "backend/app/rag/reranker.py",
    "backend/app/rag/prompt_builder.py",
    "backend/app/rag/generator.py",
    "backend/app/rag/guardrails.py",

    "backend/app/tools/order_lookup_tool.py",
    "backend/app/tools/product_lookup_tool.py",
    "backend/app/tools/return_lookup_tool.py",

    "backend/app/db/session.py",
    "backend/app/db/base.py",
    "backend/app/db/init_db.py",

    "backend/app/utils/text_cleaning.py",
    "backend/app/utils/file_loader.py",
    "backend/app/utils/logger.py",

    "frontend/streamlit_app.py",

    "scripts/download_datasets.py",
    "scripts/prepare_faq.py",
    "scripts/prepare_products.py",
    "scripts/prepare_orders.py",
    "scripts/ingest_data.py",
    "scripts/build_index.py",
    "scripts/run_eval.py",

    "notebooks/01_explore_datasets.ipynb",
    "notebooks/02_clean_and_normalize.ipynb",
    "notebooks/03_retrieval_test.ipynb",
    "notebooks/04_eval_report.ipynb",

    "docs/architecture.md",
    "docs/data_pipeline.md",
    "docs/rag_pipeline.md",
    "docs/api_design.md",
    "docs/evaluation.md"
)

foreach ($File in $Files) {
    if (-not (Test-Path $File)) {
        New-Item -ItemType File -Path $File -Force | Out-Null
        Write-Host "Created file: $File"
    } else {
        Write-Host "File already exists: $File"
    }
}

# -----------------------------
# 4. Add __init__.py files for Python packages
# -----------------------------
$InitFiles = @(
    "backend/app/__init__.py",
    "backend/app/api/__init__.py",
    "backend/app/api/v1/__init__.py",
    "backend/app/schemas/__init__.py",
    "backend/app/models/__init__.py",
    "backend/app/repositories/__init__.py",
    "backend/app/services/__init__.py",
    "backend/app/rag/__init__.py",
    "backend/app/tools/__init__.py",
    "backend/app/db/__init__.py",
    "backend/app/utils/__init__.py"
)

foreach ($InitFile in $InitFiles) {
    if (-not (Test-Path $InitFile)) {
        New-Item -ItemType File -Path $InitFile -Force | Out-Null
        Write-Host "Created Python package file: $InitFile"
    } else {
        Write-Host "Python package file already exists: $InitFile"
    }
}

# -----------------------------
# 5. Add .gitkeep for empty data folders
# -----------------------------
$GitKeepFolders = @(
    "data/external",
    "data/raw",
    "data/processed",
    "data/evaluation"
)

foreach ($Folder in $GitKeepFolders) {
    $GitKeepPath = Join-Path $Folder ".gitkeep"

    if (-not (Test-Path $GitKeepPath)) {
        New-Item -ItemType File -Path $GitKeepPath -Force | Out-Null
        Write-Host "Created .gitkeep: $GitKeepPath"
    } else {
        Write-Host ".gitkeep already exists: $GitKeepPath"
    }
}

Write-Host ""
Write-Host "ShopMind RAG project structure is ready."
Write-Host "Current path: $(Get-Location)"