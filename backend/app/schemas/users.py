from pydantic import BaseModel, Field


class PermissionSummary(BaseModel):
    id: str
    codigo: str
    nombre: str
    modulo: str = ""
    accion: str = ""
    descripcion: str = ""
    estado: bool = True


class RoleSummary(BaseModel):
    id: str
    codigo: str
    nombre: str
    descripcion: str = ""
    estado: bool = True
    permission_ids: list[str] = Field(default_factory=list)


class UserSummary(BaseModel):
    id: str
    username: str
    name: str = ""
    last_name: str = ""
    fullname: str = ""
    email: str = ""
    area: str = ""
    is_active: bool = True
    role_ids: list[str] = Field(default_factory=list)
    permission_ids: list[str] = Field(default_factory=list)
    effective_permission_ids: list[str] = Field(default_factory=list)


class AccessCatalogResponse(BaseModel):
    ok: bool
    users: list[UserSummary] = Field(default_factory=list)
    roles: list[RoleSummary] = Field(default_factory=list)
    permissions: list[PermissionSummary] = Field(default_factory=list)


class UserUpsertRequest(BaseModel):
    username: str = Field(min_length=1)
    password_hash: str | None = None
    name: str = ""
    last_name: str = ""
    email: str = ""
    area: str = ""
    is_active: bool = True
    role_ids: list[str] = Field(default_factory=list)
    permission_ids: list[str] = Field(default_factory=list)


class UserStatusRequest(BaseModel):
    is_active: bool


class UserAccessRequest(BaseModel):
    role_ids: list[str] = Field(default_factory=list)
    permission_ids: list[str] = Field(default_factory=list)


class RolePermissionsRequest(BaseModel):
    permission_ids: list[str] = Field(default_factory=list)


class MutationResponse(BaseModel):
    ok: bool
    message: str
    user: UserSummary | None = None
    role: RoleSummary | None = None
