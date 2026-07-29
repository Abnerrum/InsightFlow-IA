from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ConversaIA, Departamento, Registro
from app.schemas import PerguntaIA
from app.security import encrypt_text
from app.services.audit_service import registrar_auditoria
from app.services.openai_service import gerar_analise

router = APIRouter(prefix="/assistente", tags=["Assistente IA"])
templates = Jinja2Templates(directory="app/templates")


def resumo_dados(db: Session) -> str:
    linhas = db.execute(
        select(
            Departamento.nome,
            func.count(Registro.id).label("total"),
            func.sum(case((Registro.status == "Atrasado", 1), else_=0)).label("atrasados"),
            func.sum(case((Registro.status == "Concluído", 1), else_=0)).label("concluidos"),
            func.coalesce(func.sum(Registro.valor), 0).label("valor_total"),
        ).outerjoin(Registro).group_by(Departamento.id, Departamento.nome)
    ).all()
    if not linhas:
        return "Não existem registros cadastrados."
    return "\n".join(
        f"Departamento: {nome}; total: {total}; atrasados: {atrasados or 0}; concluídos: {concluidos or 0}; valor total: R$ {float(valor):,.2f}."
        for nome, total, atrasados, concluidos, valor in linhas
    )


@router.get("")
def pagina_assistente(request: Request):
    return templates.TemplateResponse("assistente.html", {"request": request})


@router.post("/perguntar")
def perguntar(
    entrada: PerguntaIA,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        resposta = gerar_analise(entrada.pergunta, resumo_dados(db))
        db.add(
            ConversaIA(
                pergunta=encrypt_text(entrada.pergunta),
                resposta=encrypt_text(resposta),
                criptografado=True,
            )
        )
        registrar_auditoria(db, request, "consultar_ia", "conversa_ia")
        db.commit()
    except RuntimeError as erro:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(erro)) from erro

    return {"pergunta": entrada.pergunta, "resposta": resposta}
