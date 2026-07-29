from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.database import Base, engine
from app.middleware.security import RateLimitMiddleware, RequestIdMiddleware, SecurityHeadersMiddleware
from app.routes import assistente, dashboard, importacoes, privacidade, relatorios

BASE_DIR = Path(__file__).resolve().parent
settings = get_settings()

app = FastAPI(
    title="InsightFlow IA",
    description="Sistema de análise empresarial com Python, MySQL, ChatGPT, Obsidian e controles de privacidade.",
    version="0.2.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Request-ID", "X-User-ID", "X-Admin-Key"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.include_router(dashboard.router)
app.include_router(importacoes.router)
app.include_router(assistente.router)
app.include_router(relatorios.router)
app.include_router(privacidade.router)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "titulo": "InsightFlow IA"},
    )


@app.get("/saude")
def saude():
    return {"status": "online", "sistema": "InsightFlow IA"}
