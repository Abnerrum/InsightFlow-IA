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
    valor_total = db.scalar(select(func.coalesce(func.sum(Registro.valor), 0))) or 0
    por_departamento = db.execute(
        select(
            Departamento.nome,
            func.count(Registro.id).label("total"),
            func.sum(case((Registro.status == "Atrasado", 1), else_=0)).label("atrasados"),
        ).outerjoin(Registro).group_by(Departamento.id, Departamento.nome)
    ).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total": total,
        "concluidos": concluidos,
        "atrasados": atrasados,
        "valor_total": float(valor_total),
        "por_departamento": por_departamento,
    })
