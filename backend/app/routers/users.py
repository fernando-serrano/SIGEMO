from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.collection import Collection

from app.db import (
    get_permissions_collection_dep,
    get_role_permissions_collection_dep,
    get_roles_collection_dep,
    get_user_permissions_collection_dep,
    get_user_roles_collection_dep,
    get_users_collection_dep,
)
from app.exceptions import AppException
from app.services.access_catalog import build_access_catalog_response
from app.schemas.users import (
    AccessCatalogResponse,
    MutationResponse,
    PermissionUpsertRequest,
    PermissionSummary,
    RoleUpsertRequest,
    RolePermissionsRequest,
    RoleSummary,
    UserAccessRequest,
    UserStatusRequest,
    UserSummary,
    UserUpsertRequest,
)
from app.utils.access import (
    build_object_id_candidates,
    ensure_distinct_ids,
    fetch_permission_documents_by_ids,
    fetch_role_documents_by_ids,
    get_effective_permission_ids,
    get_role_permission_ids,
    get_user_permission_ids,
    get_user_role_ids,
    parse_object_id,
)
from app.utils.security import hash_password
from app.utils.serializers import serialize_permission, serialize_role, serialize_user

router = APIRouter(prefix="/api", tags=["users"])


def sync_relation_records(
    collection: Collection,
    *,
    owner_field: str,
    owner_id: str,
    target_field: str,
    target_ids: list[str],
) -> None:
    owner_candidates = build_object_id_candidates(owner_id)
    normalized_target_ids = ensure_distinct_ids(target_ids)
    active_target_candidates = {
        target_id: build_object_id_candidates(target_id)
        for target_id in normalized_target_ids
    }

    collection.update_many(
        {owner_field: {"$in": owner_candidates}},
        {"$set": {"estado": False}},
    )

    for target_id, target_candidates in active_target_candidates.items():
        existing_relation = collection.find_one(
            {
                owner_field: {"$in": owner_candidates},
                target_field: {"$in": target_candidates},
            }
        )

        if existing_relation:
            collection.update_one(
                {"_id": existing_relation["_id"]},
                {"$set": {"estado": True, owner_field: owner_id, target_field: target_id}},
            )
            continue

        collection.insert_one({owner_field: owner_id, target_field: target_id, "estado": True})


def replace_user_roles(user_id: str, role_ids: list[str], user_roles_collection: Collection) -> None:
    sync_relation_records(
        user_roles_collection,
        owner_field="user_id",
        owner_id=user_id,
        target_field="role_id",
        target_ids=role_ids,
    )


def replace_role_users(role_id: str, user_ids: list[str], user_roles_collection: Collection) -> None:
    sync_relation_records(
        user_roles_collection,
        owner_field="role_id",
        owner_id=role_id,
        target_field="user_id",
        target_ids=user_ids,
    )


def replace_user_permissions(user_id: str, permission_ids: list[str], user_permissions_collection: Collection) -> None:
    sync_relation_records(
        user_permissions_collection,
        owner_field="user_id",
        owner_id=user_id,
        target_field="permission_id",
        target_ids=permission_ids,
    )


def replace_role_permissions(role_id: str, permission_ids: list[str], role_permissions_collection: Collection) -> None:
    normalized_permission_ids = ensure_distinct_ids(permission_ids)

    role_permissions_collection.delete_many({"role_id": {"$in": build_object_id_candidates(role_id)}})

    for permission_id in normalized_permission_ids:
        role_permissions_collection.insert_one({"role_id": role_id, "permission_id": permission_id})


def replace_permission_roles(permission_id: str, role_ids: list[str], role_permissions_collection: Collection) -> None:
    normalized_role_ids = ensure_distinct_ids(role_ids)

    role_permissions_collection.delete_many({"permission_id": {"$in": build_object_id_candidates(permission_id)}})

    for role_id in normalized_role_ids:
        role_permissions_collection.insert_one({"role_id": role_id, "permission_id": permission_id})


def replace_permission_users(permission_id: str, user_ids: list[str], user_permissions_collection: Collection) -> None:
    sync_relation_records(
        user_permissions_collection,
        owner_field="permission_id",
        owner_id=permission_id,
        target_field="user_id",
        target_ids=user_ids,
    )


def validate_role_ids(role_ids: list[str], roles_collection: Collection) -> list[str]:
    normalized_role_ids = ensure_distinct_ids(role_ids)
    role_documents = fetch_role_documents_by_ids(normalized_role_ids, roles_collection)

    if len(role_documents) != len(normalized_role_ids):
        raise ValueError("Se encontraron roles invalidos en la solicitud")

    return normalized_role_ids


def validate_permission_ids(permission_ids: list[str], permissions_collection: Collection) -> list[str]:
    normalized_permission_ids = ensure_distinct_ids(permission_ids)
    permission_documents = fetch_permission_documents_by_ids(normalized_permission_ids, permissions_collection)

    if len(permission_documents) != len(normalized_permission_ids):
        raise ValueError("Se encontraron permisos invalidos en la solicitud")

    return normalized_permission_ids


def validate_user_ids(user_ids: list[str], users_collection: Collection) -> list[str]:
    normalized_user_ids = ensure_distinct_ids(user_ids)
    candidates: list[object] = []
    for user_id in normalized_user_ids:
        candidates.extend(build_object_id_candidates(user_id))

    user_documents = list(users_collection.find({"_id": {"$in": candidates}})) if candidates else []

    if len(user_documents) != len(normalized_user_ids):
        raise ValueError("Se encontraron usuarios invalidos en la solicitud")

    return normalized_user_ids


@router.get("/access/catalog", response_model=AccessCatalogResponse)
def get_access_catalog(
    users_collection: Collection = Depends(get_users_collection_dep),
    roles_collection: Collection = Depends(get_roles_collection_dep),
    permissions_collection: Collection = Depends(get_permissions_collection_dep),
    user_roles_collection: Collection = Depends(get_user_roles_collection_dep),
    role_permissions_collection: Collection = Depends(get_role_permissions_collection_dep),
    user_permissions_collection: Collection = Depends(get_user_permissions_collection_dep),
):
    return build_access_catalog_response(
        users_collection, roles_collection, permissions_collection,
        user_roles_collection, role_permissions_collection, user_permissions_collection
    )


@router.post("/users", response_model=MutationResponse)
def create_user(
    payload: UserUpsertRequest,
    users_collection: Collection = Depends(get_users_collection_dep),
    roles_collection: Collection = Depends(get_roles_collection_dep),
    permissions_collection: Collection = Depends(get_permissions_collection_dep),
    user_roles_collection: Collection = Depends(get_user_roles_collection_dep),
    role_permissions_collection: Collection = Depends(get_role_permissions_collection_dep),
    user_permissions_collection: Collection = Depends(get_user_permissions_collection_dep),
):
    username = payload.username.strip()

    if users_collection.find_one({"username": username}):
        raise AppException(409, "Ya existe un usuario con ese username")

    try:
        role_ids = validate_role_ids(payload.role_ids, roles_collection)
        permission_ids = validate_permission_ids(payload.permission_ids, permissions_collection)
    except ValueError as error:
        raise AppException(400, str(error))

    user_document = {
        "username": username,
        "password_hash": hash_password(str(payload.password_hash or username)),
        "name": payload.name.strip(),
        "last_name": payload.last_name.strip(),
        "email": payload.email.strip(),
        "area": payload.area.strip(),
        "isActive": payload.is_active,
        "estado": payload.is_active,
    }

    insert_result = users_collection.insert_one(user_document)
    user_id = str(insert_result.inserted_id)

    replace_user_roles(user_id, role_ids, user_roles_collection)
    replace_user_permissions(user_id, permission_ids, user_permissions_collection)

    created_user = users_collection.find_one({"_id": insert_result.inserted_id})
    return MutationResponse(
        ok=True,
        message="Usuario creado correctamente",
        user=serialize_user(
            created_user or user_document,
            user_roles_collection,
            user_permissions_collection,
            role_permissions_collection,
        ),
    )


@router.put("/users/{user_id}", response_model=MutationResponse)
def update_user(
    user_id: str,
    payload: UserUpsertRequest,
    users_collection: Collection = Depends(get_users_collection_dep),
    roles_collection: Collection = Depends(get_roles_collection_dep),
    permissions_collection: Collection = Depends(get_permissions_collection_dep),
    user_roles_collection: Collection = Depends(get_user_roles_collection_dep),
    role_permissions_collection: Collection = Depends(get_role_permissions_collection_dep),
    user_permissions_collection: Collection = Depends(get_user_permissions_collection_dep),
):
    try:
        object_id = parse_object_id(user_id)
        role_ids = validate_role_ids(payload.role_ids, roles_collection)
        permission_ids = validate_permission_ids(payload.permission_ids, permissions_collection)
    except ValueError as error:
        raise AppException(400, str(error))

    existing_user = users_collection.find_one({"_id": object_id})

    if not existing_user:
        raise AppException(404, "Usuario no encontrado")

    username = payload.username.strip()
    duplicate_user = users_collection.find_one({"username": username, "_id": {"$ne": object_id}})
    if duplicate_user:
        raise AppException(409, "Ya existe otro usuario con ese username")

    update_fields = {
        "username": username,
        "name": payload.name.strip(),
        "last_name": payload.last_name.strip(),
        "email": payload.email.strip(),
        "area": payload.area.strip(),
        "isActive": payload.is_active,
        "estado": payload.is_active,
    }

    password_hash = str(payload.password_hash or "").strip()
    if password_hash:
        update_fields["password_hash"] = hash_password(password_hash)

    users_collection.update_one({"_id": object_id}, {"$set": update_fields})
    replace_user_roles(user_id, role_ids, user_roles_collection)
    replace_user_permissions(user_id, permission_ids, user_permissions_collection)

    updated_user = users_collection.find_one({"_id": object_id})
    return MutationResponse(
        ok=True,
        message="Usuario actualizado correctamente",
        user=serialize_user(updated_user or {}, user_roles_collection, user_permissions_collection, role_permissions_collection),
    )


@router.patch("/users/{user_id}/status", response_model=MutationResponse)
def update_user_status(
    user_id: str,
    payload: UserStatusRequest,
    users_collection: Collection = Depends(get_users_collection_dep),
    user_roles_collection: Collection = Depends(get_user_roles_collection_dep),
    role_permissions_collection: Collection = Depends(get_role_permissions_collection_dep),
    user_permissions_collection: Collection = Depends(get_user_permissions_collection_dep),
):
    try:
        object_id = parse_object_id(user_id)
    except ValueError as error:
        raise AppException(400, str(error))

    existing_user = users_collection.find_one({"_id": object_id})
    if not existing_user:
        raise AppException(404, "Usuario no encontrado")

    users_collection.update_one(
        {"_id": object_id},
        {"$set": {"isActive": payload.is_active, "estado": payload.is_active}},
    )

    updated_user = users_collection.find_one({"_id": object_id})
    return MutationResponse(
        ok=True,
        message="Estado de usuario actualizado",
        user=serialize_user(updated_user or {}, user_roles_collection, user_permissions_collection, role_permissions_collection),
    )


@router.put("/users/{user_id}/access", response_model=MutationResponse)
def update_user_access(
    user_id: str,
    payload: UserAccessRequest,
    users_collection: Collection = Depends(get_users_collection_dep),
    roles_collection: Collection = Depends(get_roles_collection_dep),
    permissions_collection: Collection = Depends(get_permissions_collection_dep),
    user_roles_collection: Collection = Depends(get_user_roles_collection_dep),
    role_permissions_collection: Collection = Depends(get_role_permissions_collection_dep),
    user_permissions_collection: Collection = Depends(get_user_permissions_collection_dep),
):
    try:
        object_id = parse_object_id(user_id)
        role_ids = validate_role_ids(payload.role_ids, roles_collection)
        permission_ids = validate_permission_ids(payload.permission_ids, permissions_collection)
    except ValueError as error:
        raise AppException(400, str(error))

    existing_user = users_collection.find_one({"_id": object_id})
    if not existing_user:
        raise AppException(404, "Usuario no encontrado")

    replace_user_roles(user_id, role_ids, user_roles_collection)
    replace_user_permissions(user_id, permission_ids, user_permissions_collection)

    updated_user = users_collection.find_one({"_id": object_id})
    return MutationResponse(
        ok=True,
        message="Accesos del usuario actualizados",
        user=serialize_user(updated_user or {}, user_roles_collection, user_permissions_collection, role_permissions_collection),
    )


@router.put("/roles/{role_id}/permissions", response_model=MutationResponse)
def update_role_permissions(
    role_id: str,
    payload: RolePermissionsRequest,
    roles_collection: Collection = Depends(get_roles_collection_dep),
    permissions_collection: Collection = Depends(get_permissions_collection_dep),
    role_permissions_collection: Collection = Depends(get_role_permissions_collection_dep),
    user_roles_collection: Collection = Depends(get_user_roles_collection_dep),
):
    try:
        object_id = parse_object_id(role_id)
        permission_ids = validate_permission_ids(payload.permission_ids, permissions_collection)
    except ValueError as error:
        raise AppException(400, str(error))

    existing_role = roles_collection.find_one({"_id": object_id})
    if not existing_role:
        raise AppException(404, "Rol no encontrado")

    replace_role_permissions(role_id, permission_ids, role_permissions_collection)

    updated_role = roles_collection.find_one({"_id": object_id})
    return MutationResponse(
        ok=True,
        message="Permisos del rol actualizados",
        role=serialize_role(updated_role or {}, user_roles_collection, role_permissions_collection),
    )


@router.post("/roles", response_model=MutationResponse)
def create_role(
    payload: RoleUpsertRequest,
    roles_collection: Collection = Depends(get_roles_collection_dep),
    permissions_collection: Collection = Depends(get_permissions_collection_dep),
    users_collection: Collection = Depends(get_users_collection_dep),
    user_roles_collection: Collection = Depends(get_user_roles_collection_dep),
    role_permissions_collection: Collection = Depends(get_role_permissions_collection_dep),
):
    codigo = payload.codigo.strip()
    nombre = payload.nombre.strip()

    if roles_collection.find_one({"codigo": codigo}):
        raise AppException(409, "Ya existe un rol con ese codigo")

    try:
        permission_ids = validate_permission_ids(payload.permission_ids, permissions_collection)
        user_ids = validate_user_ids(payload.user_ids, users_collection)
    except ValueError as error:
        raise AppException(400, str(error))

    role_document = {
        "codigo": codigo,
        "nombre": nombre,
        "descripcion": payload.descripcion.strip(),
        "isActive": payload.estado,
        "estado": payload.estado,
    }

    insert_result = roles_collection.insert_one(role_document)
    role_id = str(insert_result.inserted_id)

    replace_role_permissions(role_id, permission_ids, role_permissions_collection)
    replace_role_users(role_id, user_ids, user_roles_collection)

    created_role = roles_collection.find_one({"_id": insert_result.inserted_id})
    return MutationResponse(
        ok=True,
        message="Rol creado correctamente",
        role=serialize_role(created_role or role_document, user_roles_collection, role_permissions_collection),
    )


@router.put("/roles/{role_id}", response_model=MutationResponse)
def update_role(
    role_id: str,
    payload: RoleUpsertRequest,
    roles_collection: Collection = Depends(get_roles_collection_dep),
    permissions_collection: Collection = Depends(get_permissions_collection_dep),
    users_collection: Collection = Depends(get_users_collection_dep),
    user_roles_collection: Collection = Depends(get_user_roles_collection_dep),
    role_permissions_collection: Collection = Depends(get_role_permissions_collection_dep),
):
    try:
        object_id = parse_object_id(role_id)
        permission_ids = validate_permission_ids(payload.permission_ids, permissions_collection)
        user_ids = validate_user_ids(payload.user_ids, users_collection)
    except ValueError as error:
        raise AppException(400, str(error))

    existing_role = roles_collection.find_one({"_id": object_id})
    if not existing_role:
        raise AppException(404, "Rol no encontrado")

    codigo = payload.codigo.strip()
    duplicate_role = roles_collection.find_one({"codigo": codigo, "_id": {"$ne": object_id}})
    if duplicate_role:
        raise AppException(409, "Ya existe otro rol con ese codigo")

    roles_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "codigo": codigo,
                "nombre": payload.nombre.strip(),
                "descripcion": payload.descripcion.strip(),
                "isActive": payload.estado,
                "estado": payload.estado,
            }
        },
    )

    replace_role_permissions(role_id, permission_ids, role_permissions_collection)
    replace_role_users(role_id, user_ids, user_roles_collection)

    updated_role = roles_collection.find_one({"_id": object_id})
    return MutationResponse(
        ok=True,
        message="Rol actualizado correctamente",
        role=serialize_role(updated_role or {}, user_roles_collection, role_permissions_collection),
    )


@router.post("/permissions", response_model=MutationResponse)
def create_permission(
    payload: PermissionUpsertRequest,
    permissions_collection: Collection = Depends(get_permissions_collection_dep),
    roles_collection: Collection = Depends(get_roles_collection_dep),
    users_collection: Collection = Depends(get_users_collection_dep),
    role_permissions_collection: Collection = Depends(get_role_permissions_collection_dep),
    user_permissions_collection: Collection = Depends(get_user_permissions_collection_dep),
):
    codigo = payload.codigo.strip()
    nombre = payload.nombre.strip()

    if permissions_collection.find_one({"codigo": codigo}):
        raise AppException(409, "Ya existe un permiso con ese codigo")

    try:
        role_ids = validate_role_ids(payload.role_ids, roles_collection)
        user_ids = validate_user_ids(payload.user_ids, users_collection)
    except ValueError as error:
        raise AppException(400, str(error))

    permission_document = {
        "codigo": codigo,
        "nombre": nombre,
        "modulo": payload.modulo.strip(),
        "accion": payload.accion.strip(),
        "descripcion": payload.descripcion.strip(),
        "isActive": payload.estado,
        "estado": payload.estado,
    }

    insert_result = permissions_collection.insert_one(permission_document)
    permission_id = str(insert_result.inserted_id)

    replace_permission_roles(permission_id, role_ids, role_permissions_collection)
    replace_permission_users(permission_id, user_ids, user_permissions_collection)

    created_permission = permissions_collection.find_one({"_id": insert_result.inserted_id})
    return MutationResponse(
        ok=True,
        message="Permiso creado correctamente",
        permission=serialize_permission(created_permission or permission_document, role_permissions_collection, user_permissions_collection),
    )


@router.put("/permissions/{permission_id}", response_model=MutationResponse)
def update_permission(
    permission_id: str,
    payload: PermissionUpsertRequest,
    permissions_collection: Collection = Depends(get_permissions_collection_dep),
    roles_collection: Collection = Depends(get_roles_collection_dep),
    users_collection: Collection = Depends(get_users_collection_dep),
    role_permissions_collection: Collection = Depends(get_role_permissions_collection_dep),
    user_permissions_collection: Collection = Depends(get_user_permissions_collection_dep),
):
    try:
        object_id = parse_object_id(permission_id)
        role_ids = validate_role_ids(payload.role_ids, roles_collection)
        user_ids = validate_user_ids(payload.user_ids, users_collection)
    except ValueError as error:
        raise AppException(400, str(error))

    existing_permission = permissions_collection.find_one({"_id": object_id})
    if not existing_permission:
        raise AppException(404, "Permiso no encontrado")

    codigo = payload.codigo.strip()
    duplicate_permission = permissions_collection.find_one({"codigo": codigo, "_id": {"$ne": object_id}})
    if duplicate_permission:
        raise AppException(409, "Ya existe otro permiso con ese codigo")

    permissions_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "codigo": codigo,
                "nombre": payload.nombre.strip(),
                "modulo": payload.modulo.strip(),
                "accion": payload.accion.strip(),
                "descripcion": payload.descripcion.strip(),
                "isActive": payload.estado,
                "estado": payload.estado,
            }
        },
    )

    replace_permission_roles(permission_id, role_ids, role_permissions_collection)
    replace_permission_users(permission_id, user_ids, user_permissions_collection)

    updated_permission = permissions_collection.find_one({"_id": object_id})
    return MutationResponse(
        ok=True,
        message="Permiso actualizado correctamente",
        permission=serialize_permission(updated_permission or {}, role_permissions_collection, user_permissions_collection),
    )
