from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db import get_users_collection
from app.schemas.auth import LoginRequest, LoginResponse, LoginUser

router = APIRouter(prefix="/api", tags=["auth"])


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

    response_user = LoginUser(
        id=str(user.get("_id")),
        username=str(user.get("username", "")),
        fullname=str(user.get("fullname", "")),
        email=str(user.get("email", "")),
        area=str(user.get("area", "")),
        rol_id=str(user.get("rol_id")) if user.get("rol_id") is not None else None,
    )

    return LoginResponse(ok=True, user=response_user)
