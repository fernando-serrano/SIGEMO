# Frontend Specs

Directorio de especificaciones tecnicas del frontend MGA GADSO / SIGEMO.

Las specs documentan decisiones de arquitectura Vue, limites entre modulos, criterios de calidad y refactors seguros. Cada feature debe conservar su logica propia y mover a `shared/` solo infraestructura o componentes realmente reutilizables.

## Convencion

- `NNNN-nombre-corto.md`: especificacion vigente o propuesta.
- Mantener secciones: contexto, objetivo, no objetivos, alcance, criterios de aceptacion, impacto y siguientes pasos.
- Si una spec mueve logica entre carpetas, indicar el criterio de ownership.

## Specs Actuales

- `0001-frontend-architecture-boundaries.md`: auditoria y refactor de boundaries para sesion, HTTP y sidebar responsive.
