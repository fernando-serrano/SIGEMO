# Spec 0001 - Guardrails Operativos Para Jobs ESTADOS-GADSO

## Contexto

La API FastAPI ejecuta el flujo `ESTADOS-GADSO` como un subprocess Python/Playwright. El flujo de negocio, scraping, extraccion, reglas de cursos/licencias/historial y generacion de Excel viven dentro de `backend/ESTADOS-GADSO/src/agents_flow`.

Antes de esta spec, la API podia iniciar ejecuciones concurrentes sin limite explicito y asociaba resultados buscando el lote mas reciente. Ese enfoque es aceptable para pruebas o una sola corrida, pero aumenta riesgo operativo cuando varios usuarios disparan procesos cercanos en el tiempo.

## Objetivo

Agregar mitigaciones de estabilidad alrededor del job sin cambiar la logica funcional del bot:

- Limitar concurrencia de ejecuciones SUCAMEC desde la API.
- Asociar cada job con una carpeta de salida deterministica.
- Registrar metadatos operativos utiles para auditoria y soporte.
- Cancelar procesos que excedan un timeout configurable.
- Reducir ruido de archivos runtime/cache en Git.

## No Objetivos

- No cambiar selectores, navegacion ni parsing de SUCAMEC.
- No cambiar columnas del Excel de entrada o salida.
- No cambiar reglas de negocio de cursos, licencias, historial ni DSSP.
- No introducir cola distribuida, Redis, Celery, storage externo ni autenticacion nueva.
- No modificar pantallas ni contratos HTTP existentes del frontend.

## Alcance Implementado

### Concurrencia

La API valida la cantidad de jobs activos (`queued` o `running`) antes de crear una nueva ejecucion.

Variable:

```env
ESTADOS_GADSO_MAX_CONCURRENT_JOBS=1
```

Valor por defecto: `1`.

### Timeout

Cada subprocess SUCAMEC tiene un temporizador operativo. Si excede el tiempo configurado, la API termina el arbol de procesos y marca la ejecucion como error.

Variable:

```env
ESTADOS_GADSO_JOB_TIMEOUT_MINUTES=120
```

Valor por defecto: `120`.

### Salida Deterministica

La API genera un nombre de corrida:

```text
api_<yyyymmdd_hhmmss>_<job_prefix>
```

Ese valor se pasa al flujo con:

```env
SUCAMEC_RUN_NAME=<run_name>
```

`RunLoggers` respeta esa variable cuando no recibe `run_name` explicito. Como el orquestador usa el mismo `run_name` para logs y `lotes/<run_name>`, la API puede asociar el job a su carpeta esperada.

### Metadatos De Job

El JSON de runtime del job puede incluir:

- `pid`
- `input_path`
- `expected_run_name`
- `expected_output_dir`
- `result_files`
- `log_tail`

Estos campos son operativos y no forman parte de la logica de negocio.

### Lock Local

Mientras un job esta activo, la API escribe:

```text
backend/ESTADOS-GADSO/runtime/locks/estados-carne.lock
```

El lock documenta `job_id`, `grupo`, `pid`, fecha de inicio y archivo de entrada. En la etapa actual se usa como trazabilidad local y complemento del limite de concurrencia.

## Criterios De Aceptacion

- Una ejecucion nueva se rechaza si ya se alcanzo `ESTADOS_GADSO_MAX_CONCURRENT_JOBS`.
- El flujo SUCAMEC sigue recibiendo el Excel mediante `SUCAMEC_INPUT_EXCEL`.
- La carpeta de salida esperada queda asociada al job antes de ejecutar el subprocess.
- Si el subprocess excede `ESTADOS_GADSO_JOB_TIMEOUT_MINUTES`, el job termina como error operativo.
- La cancelacion manual limpia proceso, lock y upload temporal cuando corresponde.
- `npm run build` del frontend y `python -m compileall app ESTADOS-GADSO/src` del backend no fallan por estos cambios.

## Impacto Operativo

Estas mitigaciones favorecen despliegues de una sola instancia. Reducen saturacion de CPU/RAM, navegadores Playwright huerfanos y errores al descargar resultados cuando hay corridas cercanas.

Para escalamiento horizontal real, la siguiente evolucion recomendada sigue siendo mover jobs a una cola compartida y resultados a storage compartido.

## Riesgos Y Mitigaciones

- Riesgo: usuarios reciben rechazo si intentan ejecutar en paralelo.
  Mitigacion: ajustar `ESTADOS_GADSO_MAX_CONCURRENT_JOBS` segun capacidad real del servidor y estabilidad de SUCAMEC.

- Riesgo: un timeout demasiado bajo corta corridas largas validas.
  Mitigacion: iniciar con `120` minutos y ajustar con datos reales de logs.

- Riesgo: lock local no coordina multiples servidores.
  Mitigacion: documentado como guardrail local; para multiinstancia se requiere cola o lock distribuido.
