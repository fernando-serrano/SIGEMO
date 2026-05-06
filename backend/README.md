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
- `CORS_ORIGINS=http://localhost:4002,http://127.0.0.1:4002` origenes permitidos para el frontend, separados por coma.
- `ESTADOS_GADSO_DIR=./ESTADOS-GADSO`
- `ESTADOS_GADSO_PYTHON=` opcional; permite apuntar a otro interprete/venv para el flujo Playwright. Si esta vacio, la API busca automaticamente `ESTADOS-GADSO/.venv/Scripts/python.exe` en Windows o `ESTADOS-GADSO/.venv/bin/python` en Linux.
- `ESTADOS_GADSO_MAX_UPLOAD_MB=50`
- `ESTADOS_GADSO_MAX_RETAINED_UPLOADS=0` cantidad maxima de uploads temporales `entrada_*.xlsx` que se conservan aparte del upload actual. Los archivos usados por un job se eliminan al finalizar.
- `ESTADOS_GADSO_UPLOAD_TTL_MINUTES=60` tiempo maximo que puede quedar un upload temporal sin ejecutarse. Se poda automaticamente en nuevas operaciones de la API.
- `ESTADOS_GADSO_MAX_RETAINED_JOBS=10` cantidad maxima de archivos JSON de ejecuciones conservados en `ESTADOS-GADSO/runtime/jobs`. Cuando se supera el limite, se elimina el JSON mas antiguo y se mantiene el job actual.
- `ESTADOS_GADSO_MAX_CONCURRENT_JOBS=1` cantidad maxima de ejecuciones SUCAMEC activas al mismo tiempo desde la API. Protege CPU, memoria, navegadores Playwright y sesiones externas sin cambiar la logica del bot.
- `ESTADOS_GADSO_JOB_TIMEOUT_MINUTES=120` tiempo maximo permitido para una ejecucion SUCAMEC. Si se excede, la API termina el arbol de procesos y marca el job como error operativo.

Nota:

- El nombre actual de base de datos `sigemo_db` se mantiene por compatibilidad tecnica en esta etapa del refactor.
- Las credenciales del flujo SUCAMEC no se versionan. En despliegue pueden vivir como variables del entorno o en `backend/ESTADOS-GADSO/.env` dentro del workspace/servidor.

## Flujo ESTADOS-GADSO

El submodulo `SUCAMEC > ESTADOS CARNE` ejecuta el flujo Python/Playwright desde un boton del frontend:

1. El usuario carga un archivo `.xlsx`.
2. La API lo guarda en `ESTADOS-GADSO/data/entrada_data`.
3. Al ejecutar, la API crea un job en `ESTADOS-GADSO/runtime/jobs` y pasa ese archivo por `SUCAMEC_INPUT_EXCEL`. El directorio conserva solo los ultimos `ESTADOS_GADSO_MAX_RETAINED_JOBS` JSON para evitar crecimiento indefinido.
4. La API asigna un nombre de corrida deterministico `api_<timestamp>_<job>` mediante `SUCAMEC_RUN_NAME`; con esto el job queda asociado a su carpeta esperada en `ESTADOS-GADSO/lotes/`.
5. La API registra un lock operativo en `ESTADOS-GADSO/runtime/locks/estados-carne.lock` mientras el proceso esta activo. El lock es trazabilidad y proteccion local para despliegues de una sola instancia.
6. El frontend consulta el estado del job y habilita la descarga si el flujo genera resultado.
7. La descarga apunta a los archivos generados en `ESTADOS-GADSO/lotes/<corrida>/`. Si existen el Excel principal y el de validacion, se descargan juntos en un `.zip`.
8. Al finalizar el job, el Excel temporal cargado se elimina para evitar acumulacion en el servidor. Si el usuario carga y no ejecuta, el temporal expira segun `ESTADOS_GADSO_UPLOAD_TTL_MINUTES`; si carga otro archivo, se poda el anterior. La plantilla base `plantilla_mis_vigilantes.xlsx` se conserva.

Para servidores Linux/Coder, despues de instalar dependencias:

```bash
cd backend/ESTADOS-GADSO
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Si el contenedor base no trae dependencias del navegador, instalar tambien:

```bash
python -m playwright install-deps chromium
```

En Coder/Linux se recomienda usar Python 3.11 o 3.12 para el flujo OCR/Playwright. Si el venv vive fuera de `backend/ESTADOS-GADSO/.venv`, define:

```env
ESTADOS_GADSO_PYTHON=/ruta/al/venv/bin/python
```

## Ejecutar en desarrollo

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 4001
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

