from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Departamento(Base):
    __tablename__ = "departamentos"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    registros: Mapped[list["Registro"]] = relationship(back_populates="departamento")


class Registro(Base):
    __tablename__ = "registros"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    departamento_id: Mapped[int] = mapped_column(ForeignKey("departamentos.id"))
    responsavel: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    prioridade: Mapped[str] = mapped_column(String(30), default="Média")
    data_abertura: Mapped[date | None] = mapped_column(Date)
    prazo: Mapped[date | None] = mapped_column(Date)
    data_conclusao: Mapped[date | None] = mapped_column(Date)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    departamento: Mapped["Departamento"] = relationship(back_populates="registros")


class ConversaIA(Base):
    __tablename__ = "conversas_ia"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pergunta: Mapped[str] = mapped_column(Text, nullable=False)
    resposta: Mapped[str] = mapped_column(Text, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Relatorio(Base):
    __tablename__ = "relatorios"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    arquivo_markdown: Mapped[str | None] = mapped_column(String(500))
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
