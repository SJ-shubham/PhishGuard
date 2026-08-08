import sys
import os

# Allow imports from project root (for src.predictor etc.)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import create_indexes
from backend.redis_client import redis_ping


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_indexes()
    redis_ok = await redis_ping()
    print(f"[PhishGuard] MongoDB connected.")
    print(f"[PhishGuard] Redis {'connected.' if redis_ok else 'NOT reachable — some features disabled.'}")
    yield
    # Shutdown (nothing to teardown for now)


app = FastAPI(
    title="PhishGuard API",
    description="Real-time phishing URL detection API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers (added as phases complete) ────────────────────────────────────────
from backend.routes.auth  import router as auth_router
from backend.routes.scans import router as scans_router
from backend.routes.public import router as public_router

app.include_router(auth_router,   prefix="/auth",       tags=["Auth"])
app.include_router(scans_router,  prefix="/api",        tags=["Scans"])
app.include_router(public_router, prefix="/public",     tags=["Public"])


@app.get("/health", tags=["Health"])
async def health():
    redis_ok = await redis_ping()
    return {
        "status": "ok",
        "redis": "connected" if redis_ok else "unavailable",
    }
