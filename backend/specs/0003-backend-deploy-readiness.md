# Spec 0003 - Backend Deploy Readiness

## Contexto

SIGEMO / MGA GADSO opera como aplicacion interna de empresa. El perfil de riesgo no es el mismo que una aplicacion publica multi-tenant, pero el backend igual debe desplegarse con reglas minimas: configuracion reproducible, secretos fuera de Git, artefactos limpios, healthcheck y separacion clara entre runtime y desarrollo.

## Objetivo

Definir un checklist minimo para desplegar el backend sin cambiar logica de negocio ni arquitectura actual.

## No Objetivos

- No implementar JWT en esta spec.
- No introducir Celery, Redis, S3, MinIO ni observabilidad externa.
- No cambiar credenciales SUCAMEC ni su ubicacion operativa si ya existe un servidor controlado.
- No cambiar contratos del frontend.

## Politica De Credenciales

Por tratarse de una aplicacion interna, las credenciales pueden residir en el servidor operativo bajo control de la empresa, por ejemplo:

- variables de entorno del servicio;
- archivo `.env` local del servidor;
- `backend/ESTADOS-GADSO/.env` en el workspace operativo del bot.

Reglas minimas:

- No versionar `.env` ni secretos en Git.
- No publicar `.env` dentro de artefactos compartidos.
- Restringir permisos del archivo al usuario/servicio que ejecuta el backend.
- Rotar credenciales cuando se muevan entre servidores o responsables.
- Mantener `.env.example` sin valores sensibles reales.

## Checklist De Despliegue

### Runtime Backend

- Python 3.11+ instalado.
- Entorno virtual creado en el servidor.
- Dependencias instaladas con:

```bash
python -m pip install -r requirements.txt
```

- Variables configuradas:
  - `DATABASE_URL`
  - `MONGODB_DB_NAME`
  - colecciones Mongo
  - `CORS_ORIGINS`
  - `ESTADOS_GADSO_DIR`
  - `ESTADOS_GADSO_PYTHON` si el bot usa otro venv
  - limites `ESTADOS_GADSO_*`

### Runtime ESTADOS-GADSO

- Dependencias del bot instaladas en su venv.
- Chromium Playwright instalado.
- Credenciales SUCAMEC presentes en entorno controlado.
- Carpetas runtime escribibles por el usuario del servicio:
  - `ESTADOS-GADSO/data/entrada_data`
  - `ESTADOS-GADSO/runtime`
  - `ESTADOS-GADSO/lotes`
  - `ESTADOS-GADSO/logs`

### Verificacion

- `python -m compileall app ESTADOS-GADSO/src`
- `GET /api/health`
- Login con usuario interno de prueba.
- Carga de Excel de prueba.
- Ejecucion SUCAMEC controlada con pocos registros.
- Descarga de resultado.

### Quality Gate Opcional En Servidor

Para servidores donde se permita instalar dependencias dev:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
python -m ruff check app tests
```

En produccion estricta, `requirements-dev.txt` no es obligatorio.

## Artefactos Que No Deben Desplegarse Como Estado Inicial

- `__pycache__/`
- `*.pyc`
- `.coverage`
- `.pytest_cache/`
- `.pytest_tmp/`
- `pytest-cache-files-*/`
- `tests/.tmp/`
- `ESTADOS-GADSO/runtime/`
- `ESTADOS-GADSO/lotes/`
- `ESTADOS-GADSO/logs/`
- `.env` dentro de paquetes compartidos

Las carpetas runtime pueden existir en el servidor, pero deben generarse o montarse alli, no viajar como estado del repositorio.

## Criterios De Aceptacion

- El repo no trackea caches Python.
- `.gitignore` cubre caches, coverage y runtime operativo.
- El backend arranca y responde `/api/health`.
- El flujo SUCAMEC puede ejecutar una corrida de prueba.
- Las credenciales viven en servidor/entorno controlado y no en Git.

## Siguiente Evolucion

Cuando el sistema pase de una sola instancia a alta concurrencia o multiples servidores, se debe abrir una spec para:

- persistencia de jobs en Mongo;
- cola distribuida;
- storage compartido;
- locks distribuidos;
- autenticacion backend real por token o cookie segura.
