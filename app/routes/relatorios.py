from datetime import datetime
from pathlib import Path
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Relatorio
from app.schemas import RelatorioEntrada

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


def nome_seguro(texto: str) -> str:
    texto = re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚçÇ_-]+", "-", texto)
    return texto.strip("-").lower() or "relatorio"


@router.post("/exportar")
def exportar_relatorio(entrada: RelatorioEntrada, db: Session = Depends(get_db)):
    settings = get_settings()
    pasta = Path(settings.obsidian_vault_path) / "Relatorios"
    pasta.mkdir(parents=True, exist_ok=True)
    agora = datetime.now()
    arquivo = pasta / f"{agora:%Y-%m-%d_%H-%M}_{nome_seguro(entrada.titulo)}.md"
    markdown = f"""---
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
"""
    try:
        arquivo.write_text(markdown, encoding="utf-8")
    except OSError as erro:
        raise HTTPException(500, f"Falha ao salvar no Obsidian: {erro}") from erro

    db.add(Relatorio(
        titulo=entrada.titulo,
        conteudo=entrada.conteudo,
        arquivo_markdown=str(arquivo),
    ))
    db.commit()
    return {"mensagem": "Relatório exportado.", "arquivo": str(arquivo)}
