# Spec 0001 - Frontend Architecture Boundaries

## Contexto

El frontend esta construido con Vue 3, Vite y TypeScript. La estructura base ya separa `app`, `pages`, `features` y `shared`, pero habia responsabilidades transversales duplicadas en paginas y features:

- lectura/escritura de sesion en `sessionStorage`;
- logica responsive del sidebar con `window.matchMedia`;
- llamadas HTTP directas en SUCAMEC separadas del cliente comun;
- conocimiento de token repartido entre auth, router, cliente API y modulo SUCAMEC.

Para escalar modulos y submodulos, cada feature debe albergar su logica funcional, mientras `shared` debe concentrar infraestructura reutilizable y sin reglas de negocio.

## Objetivo

- Centralizar la gestion de sesion.
- Centralizar el cliente HTTP y manejo de token.
- Aislar comportamiento responsive reutilizable.
- Mantener los modulos `auth`, `users`, `sucamec`, `dashboard` y `navigation` como owners de su logica funcional.
- Evitar cambios visuales o cambios de contrato funcional.

## No Objetivos

- No introducir Pinia todavia.
- No cambiar rutas ni layout visible.
- No cambiar reglas de negocio de usuarios, roles, permisos, dashboard ni SUCAMEC.
- No dividir `UsersPage.vue` en esta spec; queda como siguiente paso por tamano y riesgo.
- No agregar librerias nuevas.

## Criterios De Ownership

### `app/`

Contiene bootstrap, router y estilos globales base. No debe contener logica funcional de modulos.

### `pages/`

Orquestan vistas y conectan route meta con features. Deben mantenerse delgadas progresivamente. Una pagina puede componer submodulos, pero no deberia concentrar reglas internas complejas cuando existe un composable de feature.

### `features/<modulo>/`

Cada modulo contiene:

- `api/`: contratos HTTP propios del modulo;
- `components/`: UI especifica del modulo/submodulo;
- `composables/`: estado y casos de uso del modulo;
- `types.ts`: tipos del modulo;
- `styles/`: estilos especificos del modulo cuando aplique.

### `shared/`

Solo infraestructura y UI reutilizable:

- cliente HTTP;
- sesion;
- layout base;
- componentes comunes;
- composables sin reglas de negocio especificas.

## Alcance Implementado

### Sesion Centralizada

Nuevo archivo:

```text
src/shared/session/session.ts
```

Responsabilidades:

- claves `sigemo-user` y `sigemo-token`;
- guardar token;
- guardar usuario;
- leer usuario;
- validar sesion activa;
- limpiar sesion.

Consumidores actualizados:

- router;
- login page;
- login API;
- sidebar;
- dashboard;
- cliente HTTP;
- SUCAMEC download URL.

### Cliente HTTP Centralizado

Archivo actualizado:

```text
src/shared/api/client.ts
```

Mejoras:

- `buildUrl` publico para descargas;
- `postForm` para `FormData`;
- `Authorization: Bearer` desde sesion compartida;
- no fuerza `Content-Type: application/json` cuando el body es `FormData`;
- limpia sesion si el backend responde `401`;
- manejo consistente de errores no OK.

### SUCAMEC Sin `fetch` Directo

Archivo actualizado:

```text
src/features/sucamec/api/estadosCarne.api.ts
```

El modulo ahora usa `apiClient` para upload, run, polling y cancelacion. La unica excepcion operacional es la URL de descarga, que se construye con `apiClient.buildUrl` y token en query param por limitacion de navegacion directa del browser.

### Sidebar Responsive Reutilizable

Nuevo archivo:

```text
src/shared/composables/useResponsiveSidebar.ts
```

Responsabilidades:

- estado `isSidebarOpen`;
- `openSidebar`;
- `closeSidebar`;
- cierre automatico al salir de viewport mobile.

Consumidores actualizados:

- `DashboardPage.vue`;
- `SucamecPage.vue`;
- `UsersPage.vue`.

## Auditoria De Estado Actual

Fortalezas:

- Buen uso de feature folders.
- Rutas lazy-loaded.
- API por modulo en `features/*/api`.
- Componentes de submodulo existentes para usuarios, roles y permisos.
- Build tipado con `vue-tsc`.

Riesgos pendientes:

- `UsersPage.vue` sigue siendo muy grande y concentra orquestacion de usuarios, roles, permisos, wizard, filtros y toasts.
- Los composables `useUserForm`, `useRoleForm`, `usePermissionForm` existen, pero `UsersPage.vue` no los consume todavia de forma completa.
- No hay tests frontend con Vitest/Testing Library.
- No hay store global; por ahora no es obligatorio, pero si el estado entre modulos crece se debe evaluar Pinia.

## Criterios De Aceptacion

- `npm run build` pasa.
- No hay `fetch` directo fuera de `shared/api/client.ts`.
- No hay acceso directo a `sigemo-user` o `sigemo-token` fuera de `shared/session/session.ts`.
- No hay `window.matchMedia` fuera de `shared/composables/useResponsiveSidebar.ts`.
- No se altera UI ni contratos funcionales.

## Siguientes Pasos Recomendados

1. Crear `0002-users-module-decomposition.md`.
2. Mover gradualmente la logica de `UsersPage.vue` a composables del feature `users`.
3. Crear `features/users/composables/useUsersPageState.ts` como fachada del modulo.
4. Agregar Vitest para `shared/session`, `shared/api` y composables puros.
5. Evaluar Pinia solo si hay estado compartido real entre modulos.
