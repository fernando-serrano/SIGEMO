from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password_hash: str = Field(min_length=1)


class LoginUser(BaseModel):
    id: str
    username: str
    name: str = ""
    last_name: str = ""
    fullname: str = ""
    email: str = ""
    area: str = ""
    rol_id: str | None = None
    role: str = ""
    role_name: str = ""


class LoginResponse(BaseModel):
    ok: bool
    message: str | None = None
    user: LoginUser | None = None
