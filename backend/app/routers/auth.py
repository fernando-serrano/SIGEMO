from fastapi import APIRouter
from fastapi.responses import JSONResponse
from bson import ObjectId
from bson.errors import InvalidId

from app.db import get_roles_collection, get_user_roles_collection, get_users_collection
from app.schemas.auth import LoginRequest, LoginResponse, LoginUser

router = APIRouter(prefix="/api", tags=["auth"])


def build_display_name(user: dict) -> tuple[str, str, str]:
    name = str(user.get("name", "")).strip()
    last_name = str(user.get("last_name", "")).strip()
    fullname = " ".join(part for part in [name, last_name] if part).strip()

    if fullname:
        return name, last_name, fullname

    legacy_fullname = str(user.get("fullname", "")).strip()
    return name, last_name, legacy_fullname


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


def resolve_user_role(user_id: object) -> tuple[str | None, str]:
    if user_id is None:
        return None, ""

    user_roles_collection = get_user_roles_collection()
    relation = None

    for candidate in build_object_id_candidates(user_id):
        relation = user_roles_collection.find_one({"user_id": candidate})
        if relation:
            break

    if not relation:
        return None, ""

    role_id = relation.get("role_id")
    if role_id is None:
        return None, ""

    roles_collection = get_roles_collection()
    for candidate in build_object_id_candidates(role_id):
        role = roles_collection.find_one({"_id": candidate})
        if role:
            return str(role.get("_id")), str(role.get("nombre", "")).strip()

    return str(role_id), ""


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    username = payload.username.strip()
    password = payload.password

    if not username or not password:
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

    if str(user.get("password", "")) != password:
        return JSONResponse(
            status_code=401,
            content={"ok": False, "message": "Credenciales invalidas"},
        )

    if user.get("isActive") is False:
        return JSONResponse(
            status_code=403,
            content={"ok": False, "message": "Usuario inactivo"},
        )

    resolved_role_id, resolved_role_name = resolve_user_role(user.get("_id"))
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
        role_name=resolved_role_name,
    )

    return LoginResponse(ok=True, user=response_user)
