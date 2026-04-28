from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db import get_roles_collection, get_user_roles_collection, get_users_collection
from app.schemas.auth import LoginRequest, LoginResponse, LoginUser
from app.utils.access import build_display_name, build_object_id_candidates, normalize_active_state

router = APIRouter(prefix="/api", tags=["auth"])


def resolve_user_role(user_id: object) -> tuple[str | None, str, str]:
    if user_id is None:
        return None, "", ""

    user_roles_collection = get_user_roles_collection()
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

    roles_collection = get_roles_collection()
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
def login(payload: LoginRequest):
    username = payload.username.strip()
    password_hash = payload.password_hash

    if not username or not password_hash:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "message": "Usuario y contrasena son obligatorios"},
        )

    user = get_users_collection().find_one({"username": username})

    if not user:
        return JSONResponse(
            status_code=401,
            content={"ok": False, "message": "Credenciales invalidas"},
        )

    if str(user.get("password_hash", "")) != password_hash:
        return JSONResponse(
            status_code=401,
            content={"ok": False, "message": "Credenciales invalidas"},
        )

    if not normalize_active_state(user):
        return JSONResponse(
            status_code=403,
            content={"ok": False, "message": "Usuario inactivo"},
        )

    resolved_role_id, resolved_role_name, resolved_role_code = resolve_user_role(user.get("_id"))
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
