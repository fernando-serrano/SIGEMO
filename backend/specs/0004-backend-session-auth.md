# Spec 0004 - Backend Session Auth

## Contexto

La aplicacion es interna de empresa, pero antes de esta spec el frontend solo guardaba `sigemo-user` en `sessionStorage` y el backend aceptaba llamadas a usuarios y SUCAMEC sin validar sesion. Eso era suficiente para prototipo, pero debil para despliegue interno con multiples usuarios.

## Objetivo

Agregar autenticacion de sesion en backend sin romper el contrato funcional existente:

- `POST /api/login` sigue aceptando `username` y `password_hash`.
- `POST /api/login` sigue devolviendo `user`.
- La respuesta agrega `access_token`, `token_type` y `expires_in`.
- El frontend guarda el token en `sessionStorage`.
- Las rutas de usuarios y SUCAMEC requieren token.

## No Objetivos

- No cambiar reglas de roles/permisos.
- No cambiar pantallas ni flujo de login visible.
- No cambiar hashing de contrasenas.
- No introducir OAuth, SSO, LDAP ni proveedor externo.
- No cambiar la logica de negocio SUCAMEC.

## Alcance Implementado

### Token

El backend emite un token firmado HS256 compatible con el formato JWT. Se implementa con libreria estandar Python para evitar una dependencia nueva en esta etapa.

Variables:

```env
AUTH_SECRET_KEY=change-this-in-server
AUTH_ACCESS_TOKEN_MINUTES=480
```

Si `AUTH_SECRET_KEY` no se define, el backend usa `DATABASE_URL` como fallback tecnico para no romper entornos existentes. En despliegue debe configurarse un secreto dedicado.

### Rutas Protegidas

Requieren sesion:

- `/api/access/catalog`
- `/api/users`
- `/api/roles`
- `/api/permissions`
- `/api/sucamec/*`

Publicas:

- `/api/login`
- `/api/health`

### Frontend

El frontend:

- guarda el token en `sessionStorage` bajo `sigemo-token`;
- mantiene `sigemo-user` para compatibilidad visual;
- envia `Authorization: Bearer <token>` desde el cliente API comun;
- envia token en llamadas directas del modulo SUCAMEC;
- adjunta `access_token` como query param en descargas, porque los links de descarga del navegador no pueden enviar headers.

## Criterios De Aceptacion

- Login existente sigue funcionando.
- Un usuario autenticado puede cargar catalogo de usuarios.
- Un usuario autenticado puede iniciar y consultar jobs SUCAMEC.
- Un request sin token a rutas privadas recibe `401`.
- Logout elimina `sigemo-user` y `sigemo-token`.
- Tests y build pasan.

## Riesgos Y Mitigaciones

- Riesgo: token en query param para descargas puede quedar en historial local.
  Mitigacion: se acepta por ahora en contexto interno; para mayor madurez se recomienda endpoint de descarga por POST, cookies HTTP-only o URLs firmadas de corta vida.

- Riesgo: no hay permisos por accion todavia.
  Mitigacion: esta spec valida sesion; una spec posterior debe aplicar autorizacion granular por permiso efectivo.

- Riesgo: fallback de secreto a `DATABASE_URL`.
  Mitigacion: mantener compatibilidad local, pero documentar `AUTH_SECRET_KEY` obligatorio en servidor.
