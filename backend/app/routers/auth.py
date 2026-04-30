from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.collection import Collection

from app.db import get_roles_collection_dep, get_user_roles_collection_dep, get_users_collection_dep
from app.exceptions import AppException
from app.schemas.auth import LoginRequest, LoginResponse, LoginUser
from app.utils.access import build_display_name, build_object_id_candidates, normalize_active_state
from app.utils.security import is_password_hash, verify_password, hash_password

router = APIRouter(prefix="/api", tags=["auth"])


def resolve_user_role(user_id: object, user_roles_collection: Collection, roles_collection: Collection) -> tuple[str | None, str, str]:
    if user_id is None:
        return None, "", ""

    relation = None

    for candidate in build_object_id_candidates(user_id):
        relation = user_roles_collection.find_one({"user_id": candidate})
        if relation:
            break

    if not relation:
        return None, "", ""

    role_id = relation.get("role_id")
    if role_id is None:
        return None, "", ""

    for candidate in build_object_id_candidates(role_id):
        role = roles_collection.find_one({"_id": candidate})
        if role:
            return (
                str(role.get("_id")),
                str(role.get("nombre", "")).strip(),
                str(role.get("codigo", "")).strip(),
            )

    return str(role_id), "", ""


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    users_collection: Collection = Depends(get_users_collection_dep),
    roles_collection: Collection = Depends(get_roles_collection_dep),
    user_roles_collection: Collection = Depends(get_user_roles_collection_dep),
):
    username = payload.username.strip()
    password_hash = payload.password_hash

    if not username or not password_hash:
        raise AppException(400, "Usuario y contrasena son obligatorios")

    user = users_collection.find_one({"username": username})

    if not user:
        raise AppException(401, "Credenciales invalidas")

    stored_password = str(user.get("password_hash", ""))
    if not verify_password(password_hash, stored_password):
        raise AppException(401, "Credenciales invalidas")

    if stored_password and not is_password_hash(stored_password):
        users_collection.update_one(
            {"_id": user.get("_id")},
            {"$set": {"password_hash": hash_password(password_hash)}},
        )

    if not normalize_active_state(user):
        raise AppException(403, "Usuario inactivo")

    resolved_role_id, resolved_role_name, resolved_role_code = resolve_user_role(user.get("_id"), user_roles_collection, roles_collection)
    name, last_name, fullname = build_display_name(user)

    response_user = LoginUser(
        id=str(user.get("_id")),
        username=str(user.get("username", "")),
        name=name,
        last_name=last_name,
        fullname=fullname,
        email=str(user.get("email", "")),
        area=str(user.get("area", "")),
        rol_id=resolved_role_id,
        role=resolved_role_code,
        role_name=resolved_role_name,
    )

    return LoginResponse(ok=True, user=response_user)
