from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import Base, engine
from app.routes import dashboard, importacoes, assistente, relatorios

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="InsightFlow IA",
    description="Sistema de análise empresarial com Python, MySQL, ChatGPT e Obsidian.",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.include_router(dashboard.router)
app.include_router(importacoes.router)
app.include_router(assistente.router)
app.include_router(relatorios.router)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "titulo": "InsightFlow IA"})


@app.get("/saude")
def saude():
    return {"status": "online", "sistema": "InsightFlow IA"}
