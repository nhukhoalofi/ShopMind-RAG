# ShopMind RAG Frontend

React + TypeScript dashboard for the ShopMind FastAPI backend.

## Run

Start Qdrant and the backend from the project root:

```powershell
uvicorn backend.app.main:app --reload
```

Then start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

Copy `.env.example` to `.env` only when the backend URL differs from
`http://localhost:8000`. No API keys belong in the frontend environment.
