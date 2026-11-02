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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(council_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
