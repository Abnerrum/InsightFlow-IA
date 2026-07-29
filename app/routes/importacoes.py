from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Departamento, Registro

router = APIRouter(prefix="/importacoes", tags=["Importações"])
templates = Jinja2Templates(directory="app/templates")

COLUNAS = {
    "departamento", "responsavel", "descricao", "status", "prioridade",
    "data_abertura", "prazo", "data_conclusao", "valor",
}


@router.get("")
def pagina_importacao(request: Request):
    return templates.TemplateResponse("importar.html", {"request": request, "mensagem": None})


@router.post("")
async def importar(request: Request, arquivo: UploadFile = File(...), db: Session = Depends(get_db)):
    nome = (arquivo.filename or "").lower()
    conteudo = await arquivo.read()
    try:
        if nome.endswith(".csv"):
            df = pd.read_csv(BytesIO(conteudo))
        elif nome.endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(conteudo))
        else:
            raise HTTPException(400, "Envie um arquivo CSV ou Excel.")
    except Exception as erro:
        raise HTTPException(400, f"Não foi possível ler o arquivo: {erro}") from erro

    df.columns = [str(c).strip().lower() for c in df.columns]
    faltantes = COLUNAS - set(df.columns)
    if faltantes:
        raise HTTPException(400, "Colunas obrigatórias ausentes: " + ", ".join(sorted(faltantes)))

    inseridos = 0
    for _, linha in df.iterrows():
        nome_departamento = str(linha["departamento"]).strip()
        departamento = db.scalar(select(Departamento).where(Departamento.nome == nome_departamento))
        if not departamento:
            departamento = Departamento(nome=nome_departamento)
            db.add(departamento)
            db.flush()

        def data_ou_none(valor):
            if pd.isna(valor) or str(valor).strip() == "":
                return None
            return pd.to_datetime(valor).date()

        db.add(Registro(
            departamento_id=departamento.id,
            responsavel=str(linha["responsavel"]).strip(),
            descricao=str(linha["descricao"]).strip(),
            status=str(linha["status"]).strip(),
            prioridade=str(linha["prioridade"]).strip(),
            data_abertura=data_ou_none(linha["data_abertura"]),
            prazo=data_ou_none(linha["prazo"]),
            data_conclusao=data_ou_none(linha["data_conclusao"]),
            valor=0 if pd.isna(linha["valor"]) else float(linha["valor"]),
        ))
        inseridos += 1

    db.commit()
    return templates.TemplateResponse("importar.html", {
        "request": request,
        "mensagem": f"{inseridos} registros importados com sucesso.",
    })
