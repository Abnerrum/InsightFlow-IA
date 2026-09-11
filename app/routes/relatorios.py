from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
import csv
import math
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Relatorio
from app.schemas import RelatorioEntrada

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])
templates = Jinja2Templates(directory="app/templates")


def nome_seguro(texto: str) -> str:
    texto = re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚçÇ_-]+", "-", texto)
    return texto.strip("-").lower() or "relatorio"


def consulta_filtrada(q: str, periodo: str):
    consulta = select(Relatorio)
    termo = q.strip()
    if termo:
        busca = f"%{termo}%"
        consulta = consulta.where(
            or_(Relatorio.titulo.ilike(busca), Relatorio.conteudo.ilike(busca))
        )
    if periodo in {"7", "30", "90"}:
        consulta = consulta.where(
            Relatorio.criado_em >= datetime.now() - timedelta(days=int(periodo))
        )
    return consulta


def relatorio_markdown(relatorio: Relatorio) -> str:
    criado_em = relatorio.criado_em or datetime.now()
    return f'''---
titulo: "{relatorio.titulo}"
data: "{criado_em:%Y-%m-%d %H:%M}"
tipo: relatorio
sistema: InsightFlow IA
---

# {relatorio.titulo}

{relatorio.conteudo}
'''


@router.get("")
def pagina_relatorios(
    request: Request,
    q: str = Query("", max_length=120),
    periodo: str = Query("todos", pattern="^(todos|7|30|90)$"),
    ordenar: str = Query("recentes", pattern="^(recentes|antigos|titulo)$"),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(9, ge=6, le=24),
    db: Session = Depends(get_db),
):
    consulta = consulta_filtrada(q, periodo)
    ordem = {
        "recentes": Relatorio.criado_em.desc(),
        "antigos": Relatorio.criado_em.asc(),
        "titulo": Relatorio.titulo.asc(),
    }[ordenar]
    total_filtrado = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    total_paginas = max(1, math.ceil(total_filtrado / por_pagina))
    pagina = min(pagina, total_paginas)
    relatorios = db.scalars(
        consulta.order_by(ordem).offset((pagina - 1) * por_pagina).limit(por_pagina)
    ).all()

    total = db.scalar(select(func.count(Relatorio.id))) or 0
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    no_mes = db.scalar(
        select(func.count(Relatorio.id)).where(Relatorio.criado_em >= inicio_mes)
    ) or 0
    ultimo = db.scalar(select(func.max(Relatorio.criado_em)))

    return templates.TemplateResponse(
        "relatorios.html",
        {
            "request": request,
            "page_title": "Central de relatórios",
            "page_subtitle": "Pesquise, visualize e exporte análises geradas pela IA.",
            "relatorios": relatorios,
            "filtros": {"q": q, "periodo": periodo, "ordenar": ordenar},
            "metricas": {"total": total, "no_mes": no_mes, "filtrados": total_filtrado, "ultimo": ultimo},
            "paginacao": {"atual": pagina, "total": total_paginas, "por_pagina": por_pagina},
        },
    )


@router.get("/exportar-csv")
def exportar_lista_csv(
    q: str = Query("", max_length=120),
    periodo: str = Query("todos", pattern="^(todos|7|30|90)$"),
    db: Session = Depends(get_db),
):
    relatorios = db.scalars(
        consulta_filtrada(q, periodo).order_by(Relatorio.criado_em.desc())
    ).all()
    arquivo = StringIO()
    writer = csv.writer(arquivo, delimiter=";")
    writer.writerow(["ID", "Título", "Conteúdo", "Criado em"])
    for item in relatorios:
        writer.writerow([item.id, item.titulo, item.conteudo, item.criado_em.strftime("%d/%m/%Y %H:%M") if item.criado_em else ""])
    return Response(
        content="\ufeff" + arquivo.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=relatorios-insightflow.csv"},
    )


@router.get("/{relatorio_id}/download")
def baixar_relatorio(
    relatorio_id: int,
    formato: str = Query("md", pattern="^(md|txt)$"),
    db: Session = Depends(get_db),
):
    relatorio = db.get(Relatorio, relatorio_id)
    if not relatorio:
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")
    conteudo = relatorio_markdown(relatorio) if formato == "md" else relatorio.conteudo
    nome = f"{nome_seguro(relatorio.titulo)}.{formato}"
    return Response(
        content=conteudo,
        media_type="text/markdown; charset=utf-8" if formato == "md" else "text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


@router.post("/exportar")
def exportar_relatorio(entrada: RelatorioEntrada, db: Session = Depends(get_db)):
    settings = get_settings()
    pasta = Path(settings.obsidian_vault_path) / "Relatorios"
    pasta.mkdir(parents=True, exist_ok=True)
    agora = datetime.now()
    arquivo = pasta / f"{agora:%Y-%m-%d_%H-%M}_{nome_seguro(entrada.titulo)}.md"
    markdown = f'''---
titulo: "{entrada.titulo}"
data: "{agora:%Y-%m-%d %H:%M}"
tipo: relatorio
sistema: InsightFlow IA
---

# {entrada.titulo}

{entrada.conteudo}

## Links internos
- [[Dashboard Geral]]
- [[Indicadores]]
- [[Planos de Ação]]
'''
    try:
        arquivo.write_text(markdown, encoding="utf-8")
    except OSError as erro:
        raise HTTPException(500, f"Falha ao salvar no Obsidian: {erro}") from erro
    db.add(Relatorio(titulo=entrada.titulo, conteudo=entrada.conteudo, arquivo_markdown=str(arquivo)))
    db.commit()
    return {"mensagem": "Relatório exportado.", "arquivo": str(arquivo)}
