# Backend FastAPI - SIGEMO

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
