from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = ""
    db_name: str = ""
    users_collection: str = "usuarios"
    roles_collection: str = "roles"
    permissions_collection: str = "permisos"
    user_roles_collection: str = "usuarios_roles"
    role_permissions_collection: str = "roles_permisos"
    user_permissions_collection: str = "usuarios_permisos"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.database_url:
            raise RuntimeError("Falta DATABASE_URL en backend/.env")
        if not self.db_name:
            self.db_name = self._infer_db_name_from_url(self.database_url)
        if not self.db_name:
            raise RuntimeError("No se pudo resolver MONGODB_DB_NAME")

    def _infer_db_name_from_url(self, url: str) -> str:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.path:
                return parsed.path.lstrip("/").strip().strip("<>")
        except Exception:
            pass
        return ""


settings = Settings()
