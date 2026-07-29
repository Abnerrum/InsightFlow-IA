from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Departamento, Registro

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def dashboard(request: Request, db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(Registro.id))) or 0
    concluidos = db.scalar(select(func.count(Registro.id)).where(Registro.status == "Concluído")) or 0
    atrasados = db.scalar(select(func.count(Registro.id)).where(Registro.status == "Atrasado")) or 0
    em_andamento = db.scalar(select(func.count(Registro.id)).where(Registro.status == "Em andamento")) or 0
    valor_total = db.scalar(select(func.coalesce(func.sum(Registro.valor), 0))) or 0
    taxa_conclusao = round((concluidos / total * 100), 1) if total else 0

    por_departamento = db.execute(
        select(
            Departamento.nome,
            func.count(Registro.id).label("total"),
            func.sum(case((Registro.status == "Atrasado", 1), else_=0)).label("atrasados"),
        )
        .outerjoin(Registro)
        .group_by(Departamento.id, Departamento.nome)
        .order_by(func.count(Registro.id).desc())
    ).all()

    recentes = db.execute(
        select(Registro, Departamento.nome)
        .join(Departamento)
        .order_by(Registro.criado_em.desc())
        .limit(8)
    ).all()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "page_title": "Dashboard executivo",
            "page_subtitle": "Acompanhe os principais indicadores da operação.",
            "total": total,
            "concluidos": concluidos,
            "atrasados": atrasados,
            "em_andamento": em_andamento,
            "valor_total": float(valor_total),
            "taxa_conclusao": taxa_conclusao,
            "por_departamento": por_departamento,
            "recentes": recentes,
            "chart_departamentos": [item.nome for item in por_departamento],
            "chart_totais": [item.total for item in por_departamento],
            "chart_atrasados": [item.atrasados or 0 for item in por_departamento],
            "chart_status": [concluidos, em_andamento, atrasados],
        },
    )
