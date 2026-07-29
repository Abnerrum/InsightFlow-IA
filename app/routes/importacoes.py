from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Departamento, Registro
from app.services.audit_service import registrar_auditoria

router = APIRouter(prefix="/importacoes", tags=["Importações"])
templates = Jinja2Templates(directory="app/templates")

COLUNAS = {
    "departamento", "responsavel", "descricao", "status", "prioridade",
    "data_abertura", "prazo", "data_conclusao", "valor",
}
TIPOS_PERMITIDOS = {
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/octet-stream",
}


def texto_seguro(valor, limite: int) -> str:
    texto = "" if pd.isna(valor) else str(valor).strip()
    if len(texto) > limite:
        raise ValueError(f"Campo excede o limite de {limite} caracteres.")
    return texto


@router.get("")
def pagina_importacao(request: Request):
    return templates.TemplateResponse("importar.html", {"request": request, "mensagem": None})


@router.post("")
async def importar(
    request: Request,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    nome = (arquivo.filename or "").lower()

    if arquivo.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(415, "Tipo de arquivo não permitido.")

    conteudo = await arquivo.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(conteudo) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Arquivo maior que {settings.max_upload_mb} MB.")

    try:
        if nome.endswith(".csv"):
            df = pd.read_csv(BytesIO(conteudo))
        elif nome.endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(conteudo))
        else:
            raise HTTPException(400, "Envie um arquivo CSV ou Excel.")
    except HTTPException:
        raise
    except Exception as erro:
        raise HTTPException(400, "Não foi possível ler o arquivo enviado.") from erro

    if len(df.index) > 50_000:
        raise HTTPException(400, "A planilha excede o limite de 50.000 linhas.")

    df.columns = [str(c).strip().lower() for c in df.columns]
    faltantes = COLUNAS - set(df.columns)
    if faltantes:
        raise HTTPException(400, "Colunas obrigatórias ausentes: " + ", ".join(sorted(faltantes)))

    inseridos = 0
    try:
        for _, linha in df.iterrows():
            nome_departamento = texto_seguro(linha["departamento"], 100)
            departamento = db.scalar(
                select(Departamento).where(Departamento.nome == nome_departamento)
            )
            if not departamento:
                departamento = Departamento(nome=nome_departamento)
                db.add(departamento)
                db.flush()

            def data_ou_none(valor):
                if pd.isna(valor) or str(valor).strip() == "":
                    return None
                return pd.to_datetime(valor, errors="raise").date()

            db.add(
                Registro(
                    departamento_id=departamento.id,
                    responsavel=texto_seguro(linha["responsavel"], 150),
                    descricao=texto_seguro(linha["descricao"], 5000),
                    status=texto_seguro(linha["status"], 50),
                    prioridade=texto_seguro(linha["prioridade"], 30),
                    data_abertura=data_ou_none(linha["data_abertura"]),
                    prazo=data_ou_none(linha["prazo"]),
                    data_conclusao=data_ou_none(linha["data_conclusao"]),
                    valor=0 if pd.isna(linha["valor"]) else float(linha["valor"]),
                )
            )
            inseridos += 1

        registrar_auditoria(
            db,
            request,
            "importar_planilha",
            nome or "arquivo_sem_nome",
            detalhes=f"registros={inseridos}",
        )
        db.commit()
    except Exception as erro:
        db.rollback()
        raise HTTPException(400, "Falha na validação ou gravação da planilha.") from erro

    return templates.TemplateResponse(
        "importar.html",
        {"request": request, "mensagem": f"{inseridos} registros importados com sucesso."},
    )
