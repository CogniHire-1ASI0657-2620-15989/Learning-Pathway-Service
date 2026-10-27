from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.configuration.settings import get_settings
from app.interfaces.rest.controller.learning_path_controller import router as learning_paths_router
from app.interfaces.rest.controller.certificate_controller import router as certificates_router


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
app.include_router(learning_paths_router)
app.include_router(certificates_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"service": "learning-pathway", "status": "healthy"}
