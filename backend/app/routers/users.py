from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db import (
    get_permissions_collection,
    get_role_permissions_collection,
    get_roles_collection,
    get_user_permissions_collection,
    get_user_roles_collection,
    get_users_collection,
)
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
    build_display_name,
    build_object_id_candidates,
    ensure_distinct_ids,
    fetch_permission_documents_by_ids,
    fetch_role_documents_by_ids,
    get_effective_permission_ids,
    get_role_permission_ids,
    get_user_permission_ids,
    get_user_role_ids,
    normalize_active_state,
    parse_object_id,
)
from app.utils.security import hash_password

router = APIRouter(prefix="/api", tags=["users"])


def serialize_permission(permission: dict) -> PermissionSummary:
    permission_id = str(permission.get("_id"))
    role_ids: list[str] = []
    for candidate in build_object_id_candidates(permission_id):
        relations = list(get_role_permissions_collection().find({"permission_id": candidate}))
        if relations:
            role_ids = ensure_distinct_ids(
                str(relation.get("role_id")) for relation in relations if relation.get("role_id") is not None
            )
            break

    user_ids: list[str] = []
    for candidate in build_object_id_candidates(permission_id):
        relations = list(get_user_permissions_collection().find({"permission_id": candidate}))
        if relations:
            user_ids = ensure_distinct_ids(
                str(relation.get("user_id")) for relation in relations if relation.get("user_id") is not None
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


def serialize_role(role: dict) -> RoleSummary:
    role_id = str(role.get("_id"))
    user_ids: list[str] = []
    for candidate in build_object_id_candidates(role_id):
        relations = list(get_user_roles_collection().find({"role_id": candidate}))
        if relations:
            user_ids = ensure_distinct_ids(
                str(relation.get("user_id")) for relation in relations if relation.get("user_id") is not None
            )
            break

    return RoleSummary(
        id=role_id,
        codigo=str(role.get("codigo", "")).strip(),
        nombre=str(role.get("nombre", "")).strip(),
        descripcion=str(role.get("descripcion", "")).strip(),
        estado=normalize_active_state(role),
        permission_ids=get_role_permission_ids(role_id),
        user_ids=user_ids,
    )


def serialize_user(user: dict) -> UserSummary:
    user_id = str(user.get("_id"))
    name, last_name, fullname = build_display_name(user)
    role_ids = get_user_role_ids(user_id)
    permission_ids = get_user_permission_ids(user_id)

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
        effective_permission_ids=get_effective_permission_ids(role_ids, permission_ids),
    )


def replace_user_roles(user_id: str, role_ids: list[str]) -> None:
    user_roles_collection = get_user_roles_collection()
    normalized_role_ids = ensure_distinct_ids(role_ids)

    user_roles_collection.delete_many({"user_id": {"$in": build_object_id_candidates(user_id)}})

    for role_id in normalized_role_ids:
        user_roles_collection.insert_one({"user_id": user_id, "role_id": role_id})


def replace_role_users(role_id: str, user_ids: list[str]) -> None:
    user_roles_collection = get_user_roles_collection()
    normalized_user_ids = ensure_distinct_ids(user_ids)

    user_roles_collection.delete_many({"role_id": {"$in": build_object_id_candidates(role_id)}})

    for user_id in normalized_user_ids:
        user_roles_collection.insert_one({"user_id": user_id, "role_id": role_id})


def replace_user_permissions(user_id: str, permission_ids: list[str]) -> None:
    user_permissions_collection = get_user_permissions_collection()
    normalized_permission_ids = ensure_distinct_ids(permission_ids)

    user_permissions_collection.delete_many({"user_id": {"$in": build_object_id_candidates(user_id)}})

    for permission_id in normalized_permission_ids:
        user_permissions_collection.insert_one({"user_id": user_id, "permission_id": permission_id})


def replace_role_permissions(role_id: str, permission_ids: list[str]) -> None:
    role_permissions_collection = get_role_permissions_collection()
    normalized_permission_ids = ensure_distinct_ids(permission_ids)

    role_permissions_collection.delete_many({"role_id": {"$in": build_object_id_candidates(role_id)}})

    for permission_id in normalized_permission_ids:
        role_permissions_collection.insert_one({"role_id": role_id, "permission_id": permission_id})


def replace_permission_roles(permission_id: str, role_ids: list[str]) -> None:
    role_permissions_collection = get_role_permissions_collection()
    normalized_role_ids = ensure_distinct_ids(role_ids)

    role_permissions_collection.delete_many({"permission_id": {"$in": build_object_id_candidates(permission_id)}})

    for role_id in normalized_role_ids:
        role_permissions_collection.insert_one({"role_id": role_id, "permission_id": permission_id})


def replace_permission_users(permission_id: str, user_ids: list[str]) -> None:
    user_permissions_collection = get_user_permissions_collection()
    normalized_user_ids = ensure_distinct_ids(user_ids)

    user_permissions_collection.delete_many({"permission_id": {"$in": build_object_id_candidates(permission_id)}})

    for user_id in normalized_user_ids:
        user_permissions_collection.insert_one({"user_id": user_id, "permission_id": permission_id})


def validate_role_ids(role_ids: list[str]) -> list[str]:
    normalized_role_ids = ensure_distinct_ids(role_ids)
    role_documents = fetch_role_documents_by_ids(normalized_role_ids)

    if len(role_documents) != len(normalized_role_ids):
        raise ValueError("Se encontraron roles invalidos en la solicitud")

    return normalized_role_ids


def validate_permission_ids(permission_ids: list[str]) -> list[str]:
    normalized_permission_ids = ensure_distinct_ids(permission_ids)
    permission_documents = fetch_permission_documents_by_ids(normalized_permission_ids)

    if len(permission_documents) != len(normalized_permission_ids):
        raise ValueError("Se encontraron permisos invalidos en la solicitud")

    return normalized_permission_ids


def validate_user_ids(user_ids: list[str]) -> list[str]:
    normalized_user_ids = ensure_distinct_ids(user_ids)
    candidates: list[object] = []
    for user_id in normalized_user_ids:
        candidates.extend(build_object_id_candidates(user_id))

    user_documents = list(get_users_collection().find({"_id": {"$in": candidates}})) if candidates else []

    if len(user_documents) != len(normalized_user_ids):
        raise ValueError("Se encontraron usuarios invalidos en la solicitud")

    return normalized_user_ids


@router.get("/access/catalog", response_model=AccessCatalogResponse)
def get_access_catalog():
    return build_access_catalog_response()


@router.post("/users", response_model=MutationResponse)
def create_user(payload: UserUpsertRequest):
    users_collection = get_users_collection()
    username = payload.username.strip()

    if users_collection.find_one({"username": username}):
        return JSONResponse(
            status_code=409,
            content={"ok": False, "message": "Ya existe un usuario con ese username"},
        )

    try:
        role_ids = validate_role_ids(payload.role_ids)
        permission_ids = validate_permission_ids(payload.permission_ids)
    except ValueError as error:
        return JSONResponse(status_code=400, content={"ok": False, "message": str(error)})

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

    replace_user_roles(user_id, role_ids)
    replace_user_permissions(user_id, permission_ids)

    created_user = users_collection.find_one({"_id": insert_result.inserted_id})
    return MutationResponse(ok=True, message="Usuario creado correctamente", user=serialize_user(created_user or user_document))


@router.put("/users/{user_id}", response_model=MutationResponse)
def update_user(user_id: str, payload: UserUpsertRequest):
    users_collection = get_users_collection()

    try:
        object_id = parse_object_id(user_id)
        role_ids = validate_role_ids(payload.role_ids)
        permission_ids = validate_permission_ids(payload.permission_ids)
    except ValueError as error:
        return JSONResponse(status_code=400, content={"ok": False, "message": str(error)})

    existing_user = users_collection.find_one({"_id": object_id})

    if not existing_user:
        return JSONResponse(status_code=404, content={"ok": False, "message": "Usuario no encontrado"})

    username = payload.username.strip()
    duplicate_user = users_collection.find_one({"username": username, "_id": {"$ne": object_id}})
    if duplicate_user:
        return JSONResponse(
            status_code=409,
            content={"ok": False, "message": "Ya existe otro usuario con ese username"},
        )

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
    replace_user_roles(user_id, role_ids)
    replace_user_permissions(user_id, permission_ids)

    updated_user = users_collection.find_one({"_id": object_id})
    return MutationResponse(ok=True, message="Usuario actualizado correctamente", user=serialize_user(updated_user or {}))


@router.patch("/users/{user_id}/status", response_model=MutationResponse)
def update_user_status(user_id: str, payload: UserStatusRequest):
    users_collection = get_users_collection()

    try:
        object_id = parse_object_id(user_id)
    except ValueError as error:
        return JSONResponse(status_code=400, content={"ok": False, "message": str(error)})

    existing_user = users_collection.find_one({"_id": object_id})
    if not existing_user:
        return JSONResponse(status_code=404, content={"ok": False, "message": "Usuario no encontrado"})

    users_collection.update_one(
        {"_id": object_id},
        {"$set": {"isActive": payload.is_active, "estado": payload.is_active}},
    )

    updated_user = users_collection.find_one({"_id": object_id})
    return MutationResponse(ok=True, message="Estado de usuario actualizado", user=serialize_user(updated_user or {}))


@router.put("/users/{user_id}/access", response_model=MutationResponse)
def update_user_access(user_id: str, payload: UserAccessRequest):
    users_collection = get_users_collection()

    try:
        object_id = parse_object_id(user_id)
        role_ids = validate_role_ids(payload.role_ids)
        permission_ids = validate_permission_ids(payload.permission_ids)
    except ValueError as error:
        return JSONResponse(status_code=400, content={"ok": False, "message": str(error)})

    existing_user = users_collection.find_one({"_id": object_id})
    if not existing_user:
        return JSONResponse(status_code=404, content={"ok": False, "message": "Usuario no encontrado"})

    replace_user_roles(user_id, role_ids)
    replace_user_permissions(user_id, permission_ids)

    updated_user = users_collection.find_one({"_id": object_id})
    return MutationResponse(ok=True, message="Accesos del usuario actualizados", user=serialize_user(updated_user or {}))


@router.put("/roles/{role_id}/permissions", response_model=MutationResponse)
def update_role_permissions(role_id: str, payload: RolePermissionsRequest):
    roles_collection = get_roles_collection()

    try:
        object_id = parse_object_id(role_id)
        permission_ids = validate_permission_ids(payload.permission_ids)
    except ValueError as error:
        return JSONResponse(status_code=400, content={"ok": False, "message": str(error)})

    existing_role = roles_collection.find_one({"_id": object_id})
    if not existing_role:
        return JSONResponse(status_code=404, content={"ok": False, "message": "Rol no encontrado"})

    replace_role_permissions(role_id, permission_ids)

    updated_role = roles_collection.find_one({"_id": object_id})
    return MutationResponse(ok=True, message="Permisos del rol actualizados", role=serialize_role(updated_role or {}))


@router.post("/roles", response_model=MutationResponse)
def create_role(payload: RoleUpsertRequest):
    roles_collection = get_roles_collection()
    codigo = payload.codigo.strip()
    nombre = payload.nombre.strip()

    if roles_collection.find_one({"codigo": codigo}):
        return JSONResponse(status_code=409, content={"ok": False, "message": "Ya existe un rol con ese codigo"})

    try:
        permission_ids = validate_permission_ids(payload.permission_ids)
        user_ids = validate_user_ids(payload.user_ids)
    except ValueError as error:
        return JSONResponse(status_code=400, content={"ok": False, "message": str(error)})

    role_document = {
        "codigo": codigo,
        "nombre": nombre,
        "descripcion": payload.descripcion.strip(),
        "isActive": payload.estado,
        "estado": payload.estado,
    }

    insert_result = roles_collection.insert_one(role_document)
    role_id = str(insert_result.inserted_id)

    replace_role_permissions(role_id, permission_ids)
    replace_role_users(role_id, user_ids)

    created_role = roles_collection.find_one({"_id": insert_result.inserted_id})
    return MutationResponse(ok=True, message="Rol creado correctamente", role=serialize_role(created_role or role_document))


@router.put("/roles/{role_id}", response_model=MutationResponse)
def update_role(role_id: str, payload: RoleUpsertRequest):
    roles_collection = get_roles_collection()

    try:
        object_id = parse_object_id(role_id)
        permission_ids = validate_permission_ids(payload.permission_ids)
        user_ids = validate_user_ids(payload.user_ids)
    except ValueError as error:
        return JSONResponse(status_code=400, content={"ok": False, "message": str(error)})

    existing_role = roles_collection.find_one({"_id": object_id})
    if not existing_role:
        return JSONResponse(status_code=404, content={"ok": False, "message": "Rol no encontrado"})

    codigo = payload.codigo.strip()
    duplicate_role = roles_collection.find_one({"codigo": codigo, "_id": {"$ne": object_id}})
    if duplicate_role:
        return JSONResponse(status_code=409, content={"ok": False, "message": "Ya existe otro rol con ese codigo"})

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

    replace_role_permissions(role_id, permission_ids)
    replace_role_users(role_id, user_ids)

    updated_role = roles_collection.find_one({"_id": object_id})
    return MutationResponse(ok=True, message="Rol actualizado correctamente", role=serialize_role(updated_role or {}))


@router.post("/permissions", response_model=MutationResponse)
def create_permission(payload: PermissionUpsertRequest):
    permissions_collection = get_permissions_collection()
    codigo = payload.codigo.strip()
    nombre = payload.nombre.strip()

    if permissions_collection.find_one({"codigo": codigo}):
        return JSONResponse(status_code=409, content={"ok": False, "message": "Ya existe un permiso con ese codigo"})

    try:
        role_ids = validate_role_ids(payload.role_ids)
        user_ids = validate_user_ids(payload.user_ids)
    except ValueError as error:
        return JSONResponse(status_code=400, content={"ok": False, "message": str(error)})

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

    replace_permission_roles(permission_id, role_ids)
    replace_permission_users(permission_id, user_ids)

    created_permission = permissions_collection.find_one({"_id": insert_result.inserted_id})
    return MutationResponse(
        ok=True,
        message="Permiso creado correctamente",
        permission=serialize_permission(created_permission or permission_document),
    )


@router.put("/permissions/{permission_id}", response_model=MutationResponse)
def update_permission(permission_id: str, payload: PermissionUpsertRequest):
    permissions_collection = get_permissions_collection()

    try:
        object_id = parse_object_id(permission_id)
        role_ids = validate_role_ids(payload.role_ids)
        user_ids = validate_user_ids(payload.user_ids)
    except ValueError as error:
        return JSONResponse(status_code=400, content={"ok": False, "message": str(error)})

    existing_permission = permissions_collection.find_one({"_id": object_id})
    if not existing_permission:
        return JSONResponse(status_code=404, content={"ok": False, "message": "Permiso no encontrado"})

    codigo = payload.codigo.strip()
    duplicate_permission = permissions_collection.find_one({"codigo": codigo, "_id": {"$ne": object_id}})
    if duplicate_permission:
        return JSONResponse(status_code=409, content={"ok": False, "message": "Ya existe otro permiso con ese codigo"})

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

    replace_permission_roles(permission_id, role_ids)
    replace_permission_users(permission_id, user_ids)

    updated_permission = permissions_collection.find_one({"_id": object_id})
    return MutationResponse(
        ok=True,
        message="Permiso actualizado correctamente",
        permission=serialize_permission(updated_permission or {}),
    )
