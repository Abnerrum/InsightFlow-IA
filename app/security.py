from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet, InvalidToken
from fastapi import Header, HTTPException, status

from app.config import get_settings


def hash_identifier(value: str) -> str:
    """Gera identificador pseudonimizado para auditoria e correlação."""
    settings = get_settings()
    secret = settings.audit_hmac_secret.encode("utf-8")
    return hmac.new(secret, value.encode("utf-8"), hashlib.sha256).hexdigest()


def _fernet() -> Fernet:
    settings = get_settings()
    if not settings.data_encryption_key:
        raise RuntimeError("DATA_ENCRYPTION_KEY não configurada.")
    return Fernet(settings.data_encryption_key.encode("utf-8"))


def encrypt_text(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_text(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except InvalidToken as error:
        raise RuntimeError("Não foi possível descriptografar o dado.") from error


def require_admin_key(x_admin_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_API_KEY não configurada.",
        )
    if not x_admin_key or not hmac.compare_digest(x_admin_key, settings.admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credencial administrativa inválida.",
        )


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def retention_limit(days: int) -> datetime:
    return utc_now() - timedelta(days=days)
