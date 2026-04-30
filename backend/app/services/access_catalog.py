from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from bson import ObjectId
from bson.errors import InvalidId

from app.db import (
    get_permissions_collection,
    get_role_permissions_collection,
    get_roles_collection,
    get_user_permissions_collection,
    get_user_roles_collection,
    get_users_collection,
)
from app.schemas.users import AccessCatalogResponse, PermissionSummary, RoleSummary, UserSummary
from app.utils.access import build_display_name, ensure_distinct_ids, normalize_active_state


def _build_lookup_candidates(values: Iterable[object]) -> list[object]:
    candidates: list[object] = []
    seen: set[str] = set()

    for value in values:
        if value is None:
            continue

        raw_value = str(value).strip()
        if not raw_value or raw_value in seen:
            continue

        seen.add(raw_value)
        candidates.append(raw_value)

        try:
            candidates.append(ObjectId(raw_value))
        except (InvalidId, TypeError):
            continue

    return candidates


def _group_relations_by_key(documents: Iterable[dict], key_name: str, value_name: str) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)

    for document in documents:
        key = document.get(key_name)
        value = document.get(value_name)

        if key is None or value is None:
            continue

        grouped[str(key)].append(str(value))

    return {key: ensure_distinct_ids(values) for key, values in grouped.items()}


def _fetch_relations_by_key(collection, key_name: str, value_name: str, source_ids: Iterable[object]) -> dict[str, list[str]]:
    candidates = _build_lookup_candidates(source_ids)
    if not candidates:
        return {}

    documents = list(collection.find({key_name: {"$in": candidates}}))
    return _group_relations_by_key(documents, key_name, value_name)


def build_access_catalog_response() -> AccessCatalogResponse:
    users = list(get_users_collection().find().sort("username", 1))
    roles = list(get_roles_collection().find().sort("nombre", 1))
    permissions = list(get_permissions_collection().find().sort([("modulo", 1), ("nombre", 1)]))

    user_ids = [user.get("_id") for user in users]
    role_ids = [role.get("_id") for role in roles]

    user_role_map = _fetch_relations_by_key(get_user_roles_collection(), "user_id", "role_id", user_ids)
    user_permission_map = _fetch_relations_by_key(get_user_permissions_collection(), "user_id", "permission_id", user_ids)
    role_permission_map = _fetch_relations_by_key(get_role_permissions_collection(), "role_id", "permission_id", role_ids)
    role_user_map = _fetch_relations_by_key(get_user_roles_collection(), "role_id", "user_id", role_ids)
    permission_role_map = _fetch_relations_by_key(
        get_role_permissions_collection(), "permission_id", "role_id", [permission.get("_id") for permission in permissions]
    )
    permission_user_map = _fetch_relations_by_key(
        get_user_permissions_collection(), "permission_id", "user_id", [permission.get("_id") for permission in permissions]
    )

    serialized_roles = [
        RoleSummary(
            id=str(role.get("_id")),
            codigo=str(role.get("codigo", "")).strip(),
            nombre=str(role.get("nombre", "")).strip(),
            descripcion=str(role.get("descripcion", "")).strip(),
            estado=normalize_active_state(role),
            permission_ids=role_permission_map.get(str(role.get("_id")), []),
            user_ids=role_user_map.get(str(role.get("_id")), []),
        )
        for role in roles
    ]

    serialized_users: list[UserSummary] = []
    for user in users:
        user_id = str(user.get("_id"))
        name, last_name, fullname = build_display_name(user)
        role_ids_for_user = user_role_map.get(user_id, [])
        direct_permission_ids = user_permission_map.get(user_id, [])

        inherited_permission_ids: list[str] = []
        for role_id in role_ids_for_user:
            inherited_permission_ids.extend(role_permission_map.get(role_id, []))

        serialized_users.append(
            UserSummary(
                id=user_id,
                username=str(user.get("username", "")).strip(),
                name=name,
                last_name=last_name,
                fullname=fullname,
                email=str(user.get("email", "")).strip(),
                area=str(user.get("area", "")).strip(),
                is_active=normalize_active_state(user),
                role_ids=role_ids_for_user,
                permission_ids=direct_permission_ids,
                effective_permission_ids=ensure_distinct_ids([*direct_permission_ids, *inherited_permission_ids]),
            )
        )

    serialized_permissions = [
        PermissionSummary(
            id=str(permission.get("_id")),
            codigo=str(permission.get("codigo", "")).strip(),
            nombre=str(permission.get("nombre", "")).strip(),
            modulo=str(permission.get("modulo", "")).strip(),
            accion=str(permission.get("accion", "")).strip(),
            descripcion=str(permission.get("descripcion", "")).strip(),
            estado=normalize_active_state(permission),
            role_ids=permission_role_map.get(str(permission.get("_id")), []),
            user_ids=permission_user_map.get(str(permission.get("_id")), []),
        )
        for permission in permissions
    ]

    return AccessCatalogResponse(
        ok=True,
        users=serialized_users,
        roles=serialized_roles,
        permissions=serialized_permissions,
    )
