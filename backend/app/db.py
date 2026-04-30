from __future__ import annotations

from pymongo import MongoClient
from pymongo.collection import Collection
from fastapi import Request

from .config import settings


_mongo_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.database_url)
    return _mongo_client


def get_db():
    return get_client()[settings.db_name]


def get_users_collection():
    return get_db()[settings.users_collection]


def get_roles_collection():
    return get_db()[settings.roles_collection]


def get_permissions_collection():
    return get_db()[settings.permissions_collection]


def get_user_roles_collection():
    return get_db()[settings.user_roles_collection]


def get_role_permissions_collection():
    return get_db()[settings.role_permissions_collection]


def get_user_permissions_collection():
    return get_db()[settings.user_permissions_collection]


# Dependency injection functions for FastAPI
def get_users_collection_dep(request: Request) -> Collection:
    return get_users_collection()


def get_roles_collection_dep(request: Request) -> Collection:
    return get_roles_collection()


def get_permissions_collection_dep(request: Request) -> Collection:
    return get_permissions_collection()


def get_user_roles_collection_dep(request: Request) -> Collection:
    return get_user_roles_collection()


def get_role_permissions_collection_dep(request: Request) -> Collection:
    return get_role_permissions_collection()


def get_user_permissions_collection_dep(request: Request) -> Collection:
    return get_user_permissions_collection()


def _ensure_relation_indexes(collection: Collection, field_name: str) -> None:
    collection.create_index(field_name)


def ensure_indexes() -> None:
    get_users_collection().create_index("username", unique=True)
    _ensure_relation_indexes(get_user_roles_collection(), "user_id")
    _ensure_relation_indexes(get_user_roles_collection(), "role_id")
    _ensure_relation_indexes(get_user_permissions_collection(), "user_id")
    _ensure_relation_indexes(get_user_permissions_collection(), "permission_id")
    _ensure_relation_indexes(get_role_permissions_collection(), "role_id")
    _ensure_relation_indexes(get_role_permissions_collection(), "permission_id")
    get_roles_collection().create_index("codigo")
    get_permissions_collection().create_index("codigo")


def ping() -> None:
    get_db().command({"ping": 1})


def close_client() -> None:
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
