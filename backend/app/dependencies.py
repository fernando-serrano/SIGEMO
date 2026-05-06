from __future__ import annotations

from typing import Annotated

from fastapi import Header, Query

from app.config import settings
from app.exceptions import AppException
from app.utils.auth_tokens import TokenError, decode_access_token


def require_auth(
    authorization: Annotated[str | None, Header()] = None,
    access_token: Annotated[str | None, Query()] = None,
) -> dict:
    scheme, _, header_token = str(authorization or "").partition(" ")
    token = header_token if scheme.lower() == "bearer" else str(access_token or "")
    if not token:
        raise AppException(401, "Sesion requerida")

    try:
        return decode_access_token(token, secret_key=settings.auth_secret_key)
    except TokenError as error:
        raise AppException(401, str(error)) from error
