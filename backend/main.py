import sys
from pathlib import Path

# Add project root to sys.path so 'backend.xxx' imports work cleanly on Vercel
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.council import router as council_router

app = FastAPI(
    title="Consilium",
    description="Council of LLMs deliberation engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(council_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
