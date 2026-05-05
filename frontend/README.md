# MGA GADSO Frontend

Frontend del sistema operativo `MGA GADSO` construido con Vue 3, Vite y TypeScript.

Actualmente `SIGEMO` se presenta como un modulo dentro de la plataforma, junto con otros procesos como SUCAMEC y vacaciones.

## Requisitos

- Node.js 20.19.0 o superior
- pnpm

## Instalacion

```sh
pnpm install
```
## Desarrollo

```sh
pnpm dev
```

El servidor de desarrollo queda en `http://localhost:4002` y consume la API en `http://localhost:4001`.

## Build de produccion

```sh
pnpm build
```

## Lint

```sh
pnpm lint
```

## Modulo Usuarios

La vista `USUARIOS / Usuarios` concentra el mantenimiento de usuarios, roles y permisos desde `src/pages/UsersPage.vue` y `src/features/users/components/UsersSubmodulePanel.vue`.

### Listado de usuarios

- El listado usa filtros por busqueda, rol y estado.
- La tabla muestra 6 registros por pagina y reinicia la paginacion al cambiar filtros.
- La paginacion usa `pagination pagination--sm` y el boton `Nuevo usuario` queda alineado en la misma barra inferior.
- El layout del listado usa una grilla 4-columnas: la tabla ocupa 3 columnas y el resumen derecho 1 columna, alineado con las tarjetas de resumen superiores.
- La fila seleccionada tiene fondo/acento visual para diferenciarla del hover normal.
- El panel derecho de resumen usa tipografia compacta, conserva espacio para nombres de hasta 2 lineas y acciones cortas `Editar` / `Desactivar`.
- Al deshabilitar un usuario activo se abre un modal de confirmacion usando clases del paquete `@richard-paredes-1/corp-style`: `modal-overlay`, `modal modal--danger`, `modal__header`, `modal__body`, `modal__footer`, `btn btn--outline btn--sm` y `btn btn--danger btn--sm`.

### Wizard de usuario

- Los titulos de ruta para creacion y edicion se normalizaron como `NUEVO USUARIO` y `EDITAR USUARIO`.
- El timeline usa una linea continua de progreso; los pasos completados se resaltan en verde con brillo.
- El paso `Datos` usa una grilla compacta de 3 columnas para `Username`, `Contrasena`, `Area`, `Nombres`, `Apellidos` y `Correo`.
- El campo `Usuario activo` usa la estructura de toggle del design system: `toggle toggle--success`, `toggle__input`, `toggle__track`, `toggle__thumb` y `toggle__label`.
- Las validaciones del wizard ya no se muestran como texto dentro del formulario; se envian al toast superior derecho.
- Los botones de accion del wizard quedan juntos; `Cancelar` usa el estilo danger suave y `Anterior` conserva `btn--ghost`.

### Roles y resumen final

- El paso `Roles` muestra tarjetas compactas en matriz 3x3 y pagina el resto de roles.
- Los checkboxes de roles usan la estructura del paquete: `checkbox`, `checkbox__input` y `checkbox__box`.
- El resumen final se reorganizo como una tarjeta de confirmacion con datos etiquetados (`Username`, `Correo`, `Area`, `Acceso`) y roles junto al nombre.
- Los permisos efectivos se listan en una sola grilla; cada permiso muestra el modulo como badge (`CLINICAS`, `EMOS`, `USUARIOS`, etc.) y la fuente `Heredado` / `Directo` en el texto secundario.
