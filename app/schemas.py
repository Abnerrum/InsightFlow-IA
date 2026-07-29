from pydantic import BaseModel, Field


class PerguntaIA(BaseModel):
    pergunta: str = Field(min_length=3, max_length=1000)


class RelatorioEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=200)
    conteudo: str = Field(min_length=3)
