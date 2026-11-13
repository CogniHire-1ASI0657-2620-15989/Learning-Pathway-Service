from contextlib import asynccontextmanager
from secrets import compare_digest

from fastapi import FastAPI, Request

from app.infrastructure.configuration.settings import get_settings
from app.dependencies import get_redis_cache
from app.interfaces.rest.controller.learning_path_controller import router as learning_paths_router
from app.interfaces.rest.controller.certificate_controller import router as certificates_router
from app.observability import install_observability, problem_response


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_settings()
    try:
        yield
    finally:
        await get_redis_cache().close()


app = FastAPI(
    title="Learning Pathway Service",
    description="Manages PathBridge learning pathways.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(learning_paths_router)
app.include_router(certificates_router)


@app.middleware("http")
async def require_internal_api_key(request: Request, call_next):
    if request.url.path == "/health":
        return await call_next(request)
    if not compare_digest(request.headers.get("X-Internal-Api-Key", ""), get_settings().internal_api_key):
        return problem_response(
            request,
            status_code=401,
            title="Unauthorized",
            detail="Unauthorized service request.",
            problem_type="urn:pathbridge:problem:http-401",
        )
    return await call_next(request)


install_observability(app, "learning-pathway-service")


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"service": "learning-pathway", "status": "healthy"}
