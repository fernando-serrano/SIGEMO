from __future__ import annotations

from pymongo.collection import Collection

from app.schemas.users import PermissionSummary, RoleSummary, UserSummary
from app.utils.access import (
    build_display_name,
    build_object_id_candidates,
    ensure_distinct_ids,
    get_effective_permission_ids,
    get_role_permission_ids,
    get_user_permission_ids,
    get_user_role_ids,
    is_relation_active,
    normalize_active_state,
)


def serialize_permission(
    permission: dict,
    role_permissions_collection: Collection,
    user_permissions_collection: Collection,
) -> PermissionSummary:
    permission_id = str(permission.get("_id"))
    role_ids: list[str] = []
    for candidate in build_object_id_candidates(permission_id):
        relations = list(role_permissions_collection.find({"permission_id": candidate}))
        if relations:
            role_ids = ensure_distinct_ids(
                str(relation.get("role_id"))
                for relation in relations
                if relation.get("role_id") is not None and is_relation_active(relation)
            )
            break

    user_ids: list[str] = []
    for candidate in build_object_id_candidates(permission_id):
        relations = list(user_permissions_collection.find({"permission_id": candidate}))
        if relations:
            user_ids = ensure_distinct_ids(
                str(relation.get("user_id"))
                for relation in relations
                if relation.get("user_id") is not None and is_relation_active(relation)
            )
            break

    return PermissionSummary(
        id=permission_id,
        codigo=str(permission.get("codigo", "")).strip(),
        nombre=str(permission.get("nombre", "")).strip(),
        modulo=str(permission.get("modulo", "")).strip(),
        accion=str(permission.get("accion", "")).strip(),
        descripcion=str(permission.get("descripcion", "")).strip(),
        estado=normalize_active_state(permission),
        role_ids=role_ids,
        user_ids=user_ids,
    )


def serialize_role(
    role: dict,
    user_roles_collection: Collection,
    role_permissions_collection: Collection,
) -> RoleSummary:
    role_id = str(role.get("_id"))
    user_ids: list[str] = []
    for candidate in build_object_id_candidates(role_id):
        relations = list(user_roles_collection.find({"role_id": candidate}))
        if relations:
            user_ids = ensure_distinct_ids(
                str(relation.get("user_id"))
                for relation in relations
                if relation.get("user_id") is not None and is_relation_active(relation)
            )
            break

    return RoleSummary(
        id=role_id,
        codigo=str(role.get("codigo", "")).strip(),
        nombre=str(role.get("nombre", "")).strip(),
        descripcion=str(role.get("descripcion", "")).strip(),
        estado=normalize_active_state(role),
        permission_ids=get_role_permission_ids(role_id, role_permissions_collection),
        user_ids=user_ids,
    )


def serialize_user(
    user: dict,
    user_roles_collection: Collection,
    user_permissions_collection: Collection,
    role_permissions_collection: Collection,
) -> UserSummary:
    user_id = str(user.get("_id"))
    name, last_name, fullname = build_display_name(user)
    role_ids = get_user_role_ids(user_id, user_roles_collection)
    permission_ids = get_user_permission_ids(user_id, user_permissions_collection)

    return UserSummary(
        id=user_id,
        username=str(user.get("username", "")).strip(),
        name=name,
        last_name=last_name,
        fullname=fullname,
        email=str(user.get("email", "")).strip(),
        area=str(user.get("area", "")).strip(),
        is_active=normalize_active_state(user),
        role_ids=role_ids,
        permission_ids=permission_ids,
        effective_permission_ids=get_effective_permission_ids(role_ids, permission_ids, role_permissions_collection),
    )
