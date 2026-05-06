# Spec 0002 - Quality Gates Iniciales Del Backend

## Contexto

El backend ya tiene una estructura modular, pero no contaba con una red automatizada de pruebas ni linting Python. Eso aumenta el riesgo de cambios posteriores, especialmente antes de implementar autenticacion real, persistencia de jobs o cola distribuida.

Esta spec introduce una primera puerta de calidad incremental. No busca resolver toda la deuda tecnica ni exigir de inmediato el objetivo final de 70% de cobertura; busca crear una base verificable y ampliable.

## Objetivo

- Agregar dependencias dev separadas de runtime.
- Configurar `pytest` con cobertura.
- Configurar `ruff` como lint inicial.
- Cubrir funciones puras y de bajo acoplamiento.
- Documentar comandos de instalacion y verificacion.

## No Objetivos

- No cambiar reglas de negocio.
- No cambiar endpoints HTTP.
- No requerir MongoDB para ejecutar tests unitarios.
- No ejecutar Playwright ni SUCAMEC en tests unitarios.
- No migrar a ODM ni introducir dependencias de infraestructura.
- No exigir todavia cobertura del 70%.

## Alcance Implementado

### Dependencias Dev

Archivo:

```text
backend/requirements-dev.txt
```

Incluye:

- `pytest`
- `pytest-cov`
- `ruff`

### Configuracion

Archivo:

```text
backend/pyproject.toml
```

Define:

- `testpaths = ["tests"]`
- `pythonpath = ["."]`
- cobertura sobre `app`
- umbral inicial `--cov-fail-under=15`
- `ruff` con reglas base `E`, `F` y `UP`

El umbral inicial es deliberadamente bajo porque gran parte del backend actual depende de Mongo, FastAPI runtime o procesos SUCAMEC. La meta operativa es subirlo por fases.

### Tests Iniciales

Carpeta:

```text
backend/tests/
```

Cobertura inicial:

- Hashing y verificacion de contrasenas.
- Compatibilidad con passwords legacy en texto plano.
- Normalizacion de estado activo.
- Construccion de nombre visible.
- Deduplicacion de IDs.
- Candidatos `ObjectId`.
- Validacion de Excel SUCAMEC.
- Preservacion de ceros por formato Excel.
- Defaults de concurrencia y timeout de jobs.

## Criterios De Aceptacion

- `python -m pytest` ejecuta la suite sin requerir MongoDB ni SUCAMEC.
- `python -m ruff check app tests` pasa sin errores.
- La cobertura total inicial queda por encima del umbral configurado.
- Los tests no escriben archivos versionables.
- La documentacion del backend explica instalacion y comandos.

## Roadmap De Cobertura

- Fase actual: minimo 15%, enfocado en funciones puras.
- Siguiente fase: 30%, agregando tests de servicios con dobles/mocks de colecciones Mongo.
- Fase de seguridad: 45%, cubriendo login, JWT y permisos por endpoint.
- Meta productiva: 70%, antes de declarar el backend listo para produccion con cambios frecuentes.

## Riesgos Y Mitigaciones

- Riesgo: el umbral inicial sea percibido como bajo.
  Mitigacion: queda documentado como punto de partida incremental, no como meta final.

- Riesgo: `ruff` marque demasiada deuda heredada si se activan reglas amplias.
  Mitigacion: iniciar con reglas base y ampliar por spec cuando el equipo acepte la limpieza.

- Riesgo: tests acoplados a filesystem temporal fallen en Windows.
  Mitigacion: los tests actuales usan una carpeta local ignorada por Git.
