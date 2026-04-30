# Backend FastAPI - MGA GADSO

Backend del sistema operativo `MGA GADSO`, donde `SIGEMO` funciona como uno de sus modulos.

## Criterios tecnicos actuales

- API construida con FastAPI y rutas separadas por dominio.
- Acceso a MongoDB centralizado en `app/db.py`.
- Refactor inicial orientado a buenas practicas:
  - hashing de contrasenas con `pbkdf2_sha256`
  - creacion automatica de indices principales en MongoDB
  - carga del catalogo de accesos optimizada por lotes
- La API mantiene algunos nombres heredados, como `password_hash` en el payload, para no romper compatibilidad con el frontend actual.

## Requisitos

- Python 3.11+

## Configuracion recomendada

Todos los comandos se ejecutan dentro de la carpeta `backend`.

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Configura variables en `.env` (usa `.env.example` como base).

Variables relevantes:

- `MONGODB_DB_NAME=sigemo_db`
- `MONGODB_USERS_COLLECTION=usuarios`
- `MONGODB_ROLES_COLLECTION=roles`
- `MONGODB_PERMISSIONS_COLLECTION=permisos`
- `MONGODB_USER_ROLES_COLLECTION=usuarios_roles`
- `MONGODB_ROLE_PERMISSIONS_COLLECTION=roles_permisos`
- `MONGODB_USER_PERMISSIONS_COLLECTION=usuarios_permisos`

Nota:

- El nombre actual de base de datos `sigemo_db` se mantiene por compatibilidad tecnica en esta etapa del refactor.

## Ejecutar en desarrollo

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Comandos utiles
```bash
# Desactivar entorno virtual
deactivate
```

## Endpoint de login

- `POST /api/login`
- Body JSON:

```json
{
  "username": "fserrano",
  "password": "fserrano"
}

