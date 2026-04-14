from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


def _sanitize_db_name(name: str) -> str:
    return name.strip().strip("<>")


def _infer_db_name_from_url(url: str) -> str:
    try:
        parsed = urlparse(url)
    except ValueError:
        return ""

    if not parsed.path:
        return ""

    return _sanitize_db_name(parsed.path.lstrip("/"))


@dataclass(frozen=True)
class Settings:
    database_url: str
    db_name: str
    users_collection: str


_database_url = os.getenv("DATABASE_URL", "").strip()
_db_name = _sanitize_db_name(
    os.getenv("MONGODB_DB_NAME", _infer_db_name_from_url(_database_url))
)
_users_collection = os.getenv("MONGODB_USERS_COLLECTION", "users").strip() or "users"

if not _database_url:
    raise RuntimeError("Falta DATABASE_URL en backend/.env")

if not _db_name:
    raise RuntimeError("No se pudo resolver MONGODB_DB_NAME")

settings = Settings(
    database_url=_database_url,
    db_name=_db_name,
    users_collection=_users_collection,
)
