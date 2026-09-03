from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Model-Agnostic AI Orchestration Engine",
        "version": "2.0.0"
    }
