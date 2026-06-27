"""FastAPI application entrypoint.

Wires the API router, structured logging, CORS, and global exception handlers
that convert all errors into the canonical API response envelope.

Run:
    uvicorn backend.app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.api.router import api_router
from backend.app.core.config import settings
from backend.app.core.logging import configure_logging, get_logger, log_event
from backend.app.db.session import init_db
from backend.app.models.responses import APIResponse

configure_logging()
logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_event(logger, "api_startup", app=settings.app_name, env=settings.app_env)
    init_db()
    log_event(logger, "database_initialized")
    yield
    log_event(logger, "api_shutdown", app=settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Agentic Solar Farm Intelligence Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
def root() -> APIResponse:
    return APIResponse.ok({"service": settings.app_name, "docs": "/docs"})


# ── Global exception handlers (always return the envelope) ──────────────────
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    body = APIResponse.fail(code=str(exc.status_code), message=str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    body = APIResponse.fail(code="422", message="Validation error")
    body.error.message = str(exc.errors())
    return JSONResponse(status_code=422, content=body.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log_event(logger, "unhandled_exception", path=str(request.url), error=str(exc))
    body = APIResponse.fail(code="500", message="Internal server error")
    return JSONResponse(status_code=500, content=body.model_dump())
