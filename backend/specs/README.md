# Backend Specs

Directorio de especificaciones tecnicas del backend MGA GADSO / SIGEMO.

El objetivo es concentrar decisiones, alcance, riesgos y criterios de aceptacion en documentos cortos antes o junto con cambios tecnicos. Cada spec debe enfocarse en una capacidad o mitigacion concreta y evitar mezclar reglas de negocio con detalles accidentales de implementacion.

## Convencion

- `NNNN-nombre-corto.md`: especificacion vigente o propuesta.
- Mantener secciones: contexto, objetivo, no objetivos, alcance, criterios de aceptacion, impacto operativo y riesgos.
- Si una spec cambia configuracion, documentar variables de entorno y valores por defecto.
- Si una spec cambia flujo operativo, indicar si altera o no la logica de negocio.

## Specs Actuales

- `0001-estados-gadso-job-guardrails.md`: guardrails operativos para ejecuciones SUCAMEC desde FastAPI.
