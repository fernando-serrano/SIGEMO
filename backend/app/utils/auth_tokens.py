from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any


class TokenError(ValueError):
    pass


def _base64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _base64url_decode(raw: str) -> bytes:
    padding = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(f"{raw}{padding}".encode("ascii"))


def _json_dumps(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def create_access_token(
    *,
    subject: str,
    username: str,
    role: str = "",
    secret_key: str,
    expires_in_seconds: int,
) -> str:
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + max(60, expires_in_seconds),
    }
    signing_input = ".".join(
        [
            _base64url_encode(_json_dumps(header)),
            _base64url_encode(_json_dumps(payload)),
        ]
    )
    signature = hmac.new(secret_key.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{_base64url_encode(signature)}"


def decode_access_token(token: str, *, secret_key: str) -> dict[str, Any]:
    try:
        header_raw, payload_raw, signature_raw = token.split(".", 2)
    except ValueError as error:
        raise TokenError("Token invalido") from error

    signing_input = f"{header_raw}.{payload_raw}"
    expected_signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()

    try:
        received_signature = _base64url_decode(signature_raw)
    except Exception as error:
        raise TokenError("Firma invalida") from error

    if not hmac.compare_digest(received_signature, expected_signature):
        raise TokenError("Firma invalida")

    try:
        header = json.loads(_base64url_decode(header_raw))
        payload = json.loads(_base64url_decode(payload_raw))
    except Exception as error:
        raise TokenError("Token invalido") from error

    if header.get("alg") != "HS256":
        raise TokenError("Algoritmo invalido")

    expires_at = int(payload.get("exp") or 0)
    if expires_at < int(time.time()):
        raise TokenError("Token expirado")

    if not payload.get("sub"):
        raise TokenError("Token sin sujeto")

    return payload
