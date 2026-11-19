import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import CLIENT_DIST, config
from app.db.database import open_database
from app.errors import HttpError
from app.routes.items import create_item, router as items_router
from app.routes.questions import router as questions_router


def create_app(db=None) -> FastAPI:
    """Build and configure the FastAPI application.

    Tests pass an in-memory database; local process opens the SQLite file on disk.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Notify developer if OpenAI key is not configured on startup
        if os.environ.get("INBOX_TESTING") != "1" and not config.openai_key:
            print("OPENAI_API_KEY is empty. Saving and questions that need a search will return 503 until it is set.")
        yield

    app = FastAPI(lifespan=lifespan)
    app.state.db = db if db is not None else open_database(config.database_path)

    # Configure CORS for local development with Vite
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config.client_origin],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Log incoming requests and response latency
    app.middleware("http")(log_request)

    @app.get("/api/health")
    def health():
        # Health probe: ready is True (app works with OpenAI or built-in local fallback)
        has_openai = bool(config.openai_key and config.openai_key.strip().startswith("sk-"))
        return {
            "ok": True,
            "ready": True,
            "mode": "openai" if has_openai else "local",
        }

    # Client API routes
    app.include_router(items_router, prefix="/api/items")
    app.include_router(questions_router, prefix="/api/questions")

    # Assessment specification routes: POST /ingest, GET /items, POST /query
    app.include_router(items_router, prefix="/items")
    app.include_router(questions_router, prefix="/api/query")
    app.include_router(questions_router, prefix="/query")
    app.post("/ingest", status_code=201)(create_item)
    app.post("/api/ingest", status_code=201)(create_item)

    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def missing_api(path: str):
        # Consistent JSON 404 for undefined API endpoints
        raise HttpError(404, "Not found")

    index = CLIENT_DIST / "index.html"
    if index.is_file():
        assets = CLIENT_DIST / "assets"
        if assets.is_dir():
            app.mount("/assets", StaticFiles(directory=assets), name="assets")

        @app.get("/")
        def client_index():
            return FileResponse(index)

        @app.get("/{path:path}")
        def client_page(path: str):
            # Built files such as the favicon are served directly. Other paths return the app shell.
            candidate = (CLIENT_DIST / path).resolve()
            if candidate.is_file() and CLIENT_DIST.resolve() in candidate.parents:
                return FileResponse(candidate)
            return FileResponse(index)

    app.add_exception_handler(HttpError, http_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
    return app


async def log_request(request, call_next):
    if os.environ.get("INBOX_TESTING") == "1":
        return await call_next(request)
    started = time.perf_counter()
    response = await call_next(request)
    elapsed = int((time.perf_counter() - started) * 1000)
    print(f"{request.method} {request.url.path} {response.status_code} {elapsed}ms")
    return response


async def http_error_handler(request, error: HttpError):
    # 503 is a missing key, which the client already explains. Log the other server failures.
    if error.status >= 500 and error.status != 503:
        print(error)
    return JSONResponse({"error": str(error)}, status_code=error.status)


async def unexpected_error_handler(request, error: Exception):
    if isinstance(error, HttpError):
        return await http_error_handler(request, error)
    print(error)
    return JSONResponse({"error": "Something went wrong"}, status_code=500)
