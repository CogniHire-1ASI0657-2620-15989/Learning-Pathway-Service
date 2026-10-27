from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.configuration.settings import get_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_settings()
    yield


app = FastAPI(
    title="Learning Pathway Service",
    description="Manages PathBridge learning pathways.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"service": "learning-pathway", "status": "healthy"}
