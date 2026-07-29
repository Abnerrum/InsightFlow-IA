from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import ConversaIA, Relatorio, SolicitacaoTitular
from app.security import hash_identifier, require_admin_key, retention_limit
from app.services.audit_service import registrar_auditoria

router = APIRouter(prefix="/privacidade", tags=["Privacidade e LGPD"])


class SolicitacaoEntrada(BaseModel):
    identificador: str = Field(min_length=3, max_length=200)
    tipo: str = Field(pattern="^(acesso|correcao|eliminacao|portabilidade|oposicao|informacao)$")
    descricao: str = Field(min_length=10, max_length=2000)


@router.get("/aviso")
def aviso_privacidade():
    settings = get_settings()
    return {
        "controlador": settings.app_name,
        "finalidades": [
            "importar e analisar dados empresariais",
            "gerar indicadores e relatórios",
            "responder perguntas com inteligência artificial",
            "manter segurança, auditoria e prevenção a fraudes",
        ],
        "canal_do_titular": settings.privacy_contact_email,
        "retencao": {
            "conversas_ia_dias": settings.conversation_retention_days,
            "relatorios_dias": settings.report_retention_days,
        },
        "observacao": "A base legal e os prazos definitivos devem ser definidos pelo controlador conforme o uso real do sistema.",
    }


@router.post("/solicitacoes")
def criar_solicitacao(
    entrada: SolicitacaoEntrada,
    request: Request,
    db: Session = Depends(get_db),
):
    protocolo = f"LGPD-{uuid4().hex[:12].upper()}"
    db.add(
        SolicitacaoTitular(
            protocolo=protocolo,
            titular_hash=hash_identifier(entrada.identificador.strip().lower()),
            tipo=entrada.tipo,
            descricao=entrada.descricao,
        )
    )
    registrar_auditoria(db, request, "criar_solicitacao_titular", protocolo)
    db.commit()
    return {"protocolo": protocolo, "status": "Recebida"}


@router.post("/retencao/executar", dependencies=[Depends(require_admin_key)])
def executar_retencao(request: Request, db: Session = Depends(get_db)):
    settings = get_settings()
    limite_conversas = retention_limit(settings.conversation_retention_days).replace(tzinfo=None)
    limite_relatorios = retention_limit(settings.report_retention_days).replace(tzinfo=None)

    conversas = db.execute(
        delete(ConversaIA).where(ConversaIA.criado_em < limite_conversas)
    ).rowcount or 0
    relatorios = db.execute(
        delete(Relatorio).where(Relatorio.criado_em < limite_relatorios)
    ).rowcount or 0

    registrar_auditoria(
        db,
        request,
        "executar_retencao",
        "dados_pessoais",
        detalhes=f"conversas={conversas}; relatorios={relatorios}",
    )
    db.commit()
    return {"conversas_excluidas": conversas, "relatorios_excluidos": relatorios}
