from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import analyze, generate, health, teach

# Absolute path so StaticFiles works regardless of CWD (local, Vercel, Docker)
_STATIC_DIR = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db import init_db
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="MusicMakerLM",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health at root — outside versioning
    app.include_router(health.router, tags=["meta"])

    # Versioned API
    app.include_router(generate.router, prefix="/api/v1", tags=["generate"])
    app.include_router(analyze.router, prefix="/api/v1", tags=["analyze"])
    app.include_router(teach.router, prefix="/api/v1", tags=["teach"])

    # Static last — must not shadow API routes
    if _STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")

    return app


app = create_app()


def run() -> None:
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
