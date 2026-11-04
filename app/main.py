from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — u produkciji OBAVEZNO ograniči na tačan domen!
ALLOWED_ORIGINS = (
    ["*"] if settings.APP_ENV == "development"
    else settings.ALLOWED_ORIGINS.split(",")
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. API Rute
app.include_router(api_router, prefix=settings.API_V1_STR)

# 2. Frontend putanje
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

if FRONTEND_DIR.exists():
    # Mountujemo SVAKI postojeći podfolder iz frontend/ na /static/<ime>/
    for subdir in ("css", "js", "img", "fonts", "icons"):
        sub_path = FRONTEND_DIR / subdir
        if sub_path.exists() and sub_path.is_dir():
            app.mount(
                f"/static/{subdir}",
                StaticFiles(directory=str(sub_path)),
                name=f"static-{subdir}",
            )

    # --- HTML stranice ---
    @app.get("/", tags=["Frontend"])
    def serve_frontend_root():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.get("/orders", tags=["Frontend"])
    def serve_orders_page():
        return FileResponse(str(FRONTEND_DIR / "orders.html"))

    @app.get("/dashboard", tags=["Frontend"])
    def serve_dashboard_page():
        return FileResponse(str(FRONTEND_DIR / "dashboard.html"))

    @app.get("/inventory", tags=["Frontend"])
    def serve_inventory_page():
        return FileResponse(str(FRONTEND_DIR / "inventory.html"))

    @app.get("/status", tags=["Frontend"])
    def serve_status_page():
        return FileResponse(str(FRONTEND_DIR / "status.html"))

    @app.get("/reminders", tags=["Frontend"])
    def serve_reminders_page():
        return FileResponse(str(FRONTEND_DIR / "reminders.html"))

    # --- PWA fajlovi ---
    @app.get("/sw.js", tags=["PWA"])
    def serve_service_worker():
        return FileResponse(
            str(FRONTEND_DIR / "sw.js"), media_type="application/javascript"
        )

    @app.get("/manifest.json", tags=["PWA"])
    def serve_manifest():
        return FileResponse(
            str(FRONTEND_DIR / "manifest.json"), media_type="application/json"
        )


@app.get("/health", tags=["Status"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}