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
    roles_collection: str
    permissions_collection: str
    user_roles_collection: str
    role_permissions_collection: str
    user_permissions_collection: str


_database_url = os.getenv("DATABASE_URL", "").strip()
_db_name = _sanitize_db_name(
    os.getenv("MONGODB_DB_NAME", _infer_db_name_from_url(_database_url))
)
_users_collection = os.getenv("MONGODB_USERS_COLLECTION", "users").strip() or "users"
_roles_collection = os.getenv("MONGODB_ROLES_COLLECTION", "roles").strip() or "roles"
_permissions_collection = os.getenv("MONGODB_PERMISSIONS_COLLECTION", "permisos").strip() or "permisos"
_user_roles_collection = os.getenv("MONGODB_USER_ROLES_COLLECTION", "usuarios_roles").strip() or "usuarios_roles"
_role_permissions_collection = os.getenv("MONGODB_ROLE_PERMISSIONS_COLLECTION", "roles_permisos").strip() or "roles_permisos"
_user_permissions_collection = os.getenv("MONGODB_USER_PERMISSIONS_COLLECTION", "usuarios_permisos").strip() or "usuarios_permisos"

if not _database_url:
    raise RuntimeError("Falta DATABASE_URL en backend/.env")

if not _db_name:
    raise RuntimeError("No se pudo resolver MONGODB_DB_NAME")

settings = Settings(
    database_url=_database_url,
    db_name=_db_name,
    users_collection=_users_collection,
    roles_collection=_roles_collection,
    permissions_collection=_permissions_collection,
    user_roles_collection=_user_roles_collection,
    role_permissions_collection=_role_permissions_collection,
    user_permissions_collection=_user_permissions_collection,
)
