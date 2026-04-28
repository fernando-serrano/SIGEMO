from __future__ import annotations

from collections.abc import Iterable

from bson import ObjectId
from bson.errors import InvalidId

from app.db import (
    get_permissions_collection,
    get_role_permissions_collection,
    get_roles_collection,
    get_user_permissions_collection,
    get_user_roles_collection,
)


def build_object_id_candidates(value: object) -> list[object]:
    if value is None:
        return []

    candidates: list[object] = [value]
    value_as_string = str(value).strip()

    if value_as_string and value_as_string != value:
        candidates.append(value_as_string)

    if value_as_string:
        try:
            candidates.append(ObjectId(value_as_string))
        except (InvalidId, TypeError):
            pass

    return candidates


def parse_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value.strip())
    except (InvalidId, AttributeError, TypeError) as error:
        raise ValueError("Identificador invalido") from error


def build_display_name(user: dict) -> tuple[str, str, str]:
    name = str(user.get("name", "")).strip()
    last_name = str(user.get("last_name", "")).strip()
    fullname = " ".join(part for part in [name, last_name] if part).strip()

    if fullname:
        return name, last_name, fullname

    legacy_fullname = str(user.get("fullname", "")).strip()
    return name, last_name, legacy_fullname


def normalize_active_state(document: dict, *, default: bool = True) -> bool:
    if "isActive" in document:
        return bool(document.get("isActive"))

    if "estado" in document:
        return bool(document.get("estado"))

    return default


def ensure_distinct_ids(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for raw_value in values:
        value = str(raw_value).strip()
        if not value or value in seen:
            continue

        seen.add(value)
        result.append(value)

    return result


def fetch_role_documents_by_ids(role_ids: Iterable[str]) -> list[dict]:
    roles_collection = get_roles_collection()
    role_documents: list[dict] = []

    for role_id in ensure_distinct_ids(role_ids):
        for candidate in build_object_id_candidates(role_id):
            role = roles_collection.find_one({"_id": candidate})
            if role:
                role_documents.append(role)
                break

    return role_documents


def fetch_permission_documents_by_ids(permission_ids: Iterable[str]) -> list[dict]:
    permissions_collection = get_permissions_collection()
    permission_documents: list[dict] = []

    for permission_id in ensure_distinct_ids(permission_ids):
        for candidate in build_object_id_candidates(permission_id):
            permission = permissions_collection.find_one({"_id": candidate})
            if permission:
                permission_documents.append(permission)
                break

    return permission_documents


def get_user_role_ids(user_id: object) -> list[str]:
    user_roles_collection = get_user_roles_collection()
    role_ids: list[str] = []

    for candidate in build_object_id_candidates(user_id):
        relations = list(user_roles_collection.find({"user_id": candidate}))
        if relations:
            role_ids.extend(str(relation.get("role_id")) for relation in relations if relation.get("role_id") is not None)
            break

    return ensure_distinct_ids(role_ids)


def get_role_permission_ids(role_id: object) -> list[str]:
    role_permissions_collection = get_role_permissions_collection()
    permission_ids: list[str] = []

    for candidate in build_object_id_candidates(role_id):
        relations = list(role_permissions_collection.find({"role_id": candidate}))
        if relations:
            permission_ids.extend(
                str(relation.get("permission_id")) for relation in relations if relation.get("permission_id") is not None
            )
            break

    return ensure_distinct_ids(permission_ids)


def get_user_permission_ids(user_id: object) -> list[str]:
    user_permissions_collection = get_user_permissions_collection()
    permission_ids: list[str] = []

    for candidate in build_object_id_candidates(user_id):
        relations = list(user_permissions_collection.find({"user_id": candidate}))
        if relations:
            permission_ids.extend(
                str(relation.get("permission_id")) for relation in relations if relation.get("permission_id") is not None
            )
            break

    return ensure_distinct_ids(permission_ids)


def get_effective_permission_ids(role_ids: Iterable[str], direct_permission_ids: Iterable[str]) -> list[str]:
    combined_permission_ids = list(direct_permission_ids)

    for role_id in role_ids:
        combined_permission_ids.extend(get_role_permission_ids(role_id))

    return ensure_distinct_ids(combined_permission_ids)
