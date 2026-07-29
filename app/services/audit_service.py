from fastapi import Request
from sqlalchemy.orm import Session

from app.models import Auditoria
from app.security import hash_identifier


def registrar_auditoria(
    db: Session,
    request: Request,
    acao: str,
    recurso: str,
    resultado: str = "sucesso",
    detalhes: str | None = None,
) -> None:
    client = request.client.host if request.client else "unknown"
    ator = request.headers.get("X-User-ID", client)
    db.add(
        Auditoria(
            request_id=getattr(request.state, "request_id", "sem-request-id"),
            ator_hash=hash_identifier(ator),
            acao=acao,
            recurso=recurso,
            resultado=resultado,
            detalhes=detalhes,
        )
    )
