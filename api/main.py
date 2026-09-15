from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.orchestrate import router as orchestrate_router
from api.routes.health import router as health_router

app = FastAPI(
    title="Model-Agnostic AI Orchestration Engine API",
    description="Standalone, high-performance model orchestration engine for enterprise applications",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orchestrate_router)
app.include_router(health_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)

