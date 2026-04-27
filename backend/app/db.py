from __future__ import annotations

from pymongo import MongoClient

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


def get_user_roles_collection():
    return get_db()[settings.user_roles_collection]


def ping() -> None:
    get_db().command({"ping": 1})


def close_client() -> None:
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
