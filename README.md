# SIGEMO / MGA GADSO

Solucion web compuesta por dos piezas desplegables:

- `backend/`: API FastAPI, MongoDB, autenticacion, usuarios/permisos y orquestacion del flujo SUCAMEC.
- `frontend/`: aplicacion Vue compilable como archivos estaticos que consumen la API.

El frontend y el backend no comparten runtime en despliegue. El frontend se compila y se sirve como contenido web; el backend queda levantado como servicio HTTP.

## Requisitos

- Python 3.11+ para el backend.
- Python 3.11 o 3.12 recomendado para `backend/ESTADOS-GADSO`.
- Node compatible con `frontend/package.json`.
- MongoDB accesible desde el backend.
- Chromium/Playwright instalado para el flujo SUCAMEC.

## Variables

Backend:

- Crear `backend/.env` usando `backend/.env.example`.
- Configurar `DATABASE_URL`, `MONGODB_DB_NAME`, colecciones y `CORS_ORIGINS`.
- Configurar `ESTADOS_GADSO_DIR`, `ESTADOS_GADSO_PYTHON` si aplica, y limites operativos.

Flujo SUCAMEC:

- Crear `backend/ESTADOS-GADSO/.env` con credenciales SUCAMEC y correo.
- No versionar archivos `.env` ni secretos.

Frontend:

- Definir `VITE_API_BASE_URL` cuando el backend no vive en el mismo origen.

## Desarrollo Local

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 4001
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Flujo SUCAMEC en Linux/Coder

```bash
cd backend/ESTADOS-GADSO
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m playwright install-deps chromium
```

## Build de Frontend

```bash
cd frontend
npm run build
```

Publicar el contenido generado en `frontend/dist/` con un servidor estatico o reverse proxy.

## Checklist Seguro de Despliegue

1. Configurar secretos en el servidor, no en Git.
2. Instalar dependencias de backend y validar `/api/health`.
3. Instalar dependencias de `ESTADOS-GADSO` y Chromium de Playwright.
4. Configurar `CORS_ORIGINS` con la URL real del frontend.
5. Configurar `VITE_API_BASE_URL` con la URL real del backend.
6. Ejecutar `npm run build` y publicar `frontend/dist/`.
7. Probar login, usuarios/roles/permisos y carga/ejecucion/descarga de Estados SUCAMEC.
8. Revisar logs del backend y logs del flujo en `backend/ESTADOS-GADSO/logs/`.
