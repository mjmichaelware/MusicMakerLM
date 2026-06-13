from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import analyze, generate, health, teach


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db import init_db
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="MusicMakerLM",
        version="0.1.0",
        description="Generate, analyze, and teach music — symbolic core, $0 to build.",
        debug=settings.debug,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check — no versioned prefix so monitoring tools can reach it simply
    application.include_router(health.router, tags=["meta"])

    # Versioned API
    application.include_router(generate.router, prefix="/api/v1", tags=["generate"])
    application.include_router(analyze.router, prefix="/api/v1", tags=["analyze"])
    application.include_router(teach.router, prefix="/api/v1", tags=["teach"])

    # Static files MUST be last — it catches all remaining paths
    application.mount("/", StaticFiles(directory="static", html=True), name="static")

    return application


app = create_app()


def run() -> None:
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
