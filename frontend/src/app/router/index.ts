import { createRouter, createWebHistory } from 'vue-router'

const SESSION_STORAGE_KEY = 'sigemo-user'

function hasActiveSession(): boolean {
  const rawSession = sessionStorage.getItem(SESSION_STORAGE_KEY)
  if (!rawSession) return false

  try {
    const session = JSON.parse(rawSession) as { id?: string; username?: string }
    return Boolean(session.id || session.username)
  } catch {
    sessionStorage.removeItem(SESSION_STORAGE_KEY)
    return false
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('@/pages/LoginPage.vue'),
      meta: {
        public: true,
      },
    },
    {
      path: '/sucamec',
      name: 'sucamec',
      component: () => import('@/pages/SucamecPage.vue'),
      meta: {
        section: 'SUCAMEC',
        pageTitle: 'PANEL SUCAMEC',
        homeTo: '/sucamec',
        breadcrumb: [{ label: 'SUCAMEC' }, { label: 'Panel' }],
      },
    },
    {
      path: '/sucamec/estados-carne',
      name: 'sucamec-estados-carne',
      component: () => import('@/pages/SucamecPage.vue'),
      meta: {
        section: 'SUCAMEC',
        pageTitle: 'ESTADOS',
        homeTo: '/sucamec',
        sucamecSection: 'estados-carne',
        breadcrumb: [{ label: 'SUCAMEC', to: '/sucamec' }, { label: 'ESTADOS' }],
      },
    },
    {
      path: '/inicio',
      name: 'inicio',
      component: () => import('@/pages/DashboardPage.vue'),
      meta: {
        section: 'SIGEMO',
        homeTo: '/inicio',
        pageTitle: "SEGUIMIENTO EMO'S",
        breadcrumb: [{ label: 'SIGEMO' }, { label: "SEGUIMIENTO EMO'S" }],
      },
    },
    {
      path: '/usuarios',
      name: 'usuarios',
      redirect: '/usuarios/usuarios',
    },
    {
      path: '/usuarios/usuarios',
      name: 'usuarios-listado',
      component: () => import('@/pages/UsersPage.vue'),
      meta: {
        section: 'USUARIOS',
        homeTo: '/usuarios/usuarios',
        pageTitle: 'USUARIOS',
        userSection: 'usuarios',
        userMode: 'list',
        breadcrumb: [{ label: 'USUARIOS' }, { label: 'Usuarios' }],
      },
    },
    {
      path: '/usuarios/usuarios/nuevo/datos',
      name: 'usuarios-nuevo-datos',
      component: () => import('@/pages/UsersPage.vue'),
      meta: {
        section: 'USUARIOS',
        homeTo: '/usuarios/usuarios',
        pageTitle: 'NUEVO USUARIO',
        userSection: 'usuarios',
        userMode: 'create',
        userStep: 'datos',
        breadcrumb: [{ label: 'USUARIOS', to: '/usuarios/usuarios' }, { label: 'Nuevo usuario' }, { label: 'Datos' }],
      },
    },
    {
      path: '/usuarios/usuarios/nuevo/roles',
      name: 'usuarios-nuevo-roles',
      component: () => import('@/pages/UsersPage.vue'),
      meta: {
        section: 'USUARIOS',
        homeTo: '/usuarios/usuarios',
        pageTitle: 'NUEVO USUARIO',
        userSection: 'usuarios',
        userMode: 'create',
        userStep: 'roles',
        breadcrumb: [{ label: 'USUARIOS', to: '/usuarios/usuarios' }, { label: 'Nuevo usuario' }, { label: 'Roles' }],
      },
    },
    {
      path: '/usuarios/usuarios/nuevo/permisos',
      name: 'usuarios-nuevo-permisos',
      component: () => import('@/pages/UsersPage.vue'),
      meta: {
        section: 'USUARIOS',
        homeTo: '/usuarios/usuarios',
        pageTitle: 'NUEVO USUARIO',
        userSection: 'usuarios',
        userMode: 'create',
        userStep: 'permisos',
        breadcrumb: [{ label: 'USUARIOS', to: '/usuarios/usuarios' }, { label: 'Nuevo usuario' }, { label: 'Permisos' }],
      },
    },
    {
      path: '/usuarios/usuarios/nuevo/resumen',
      name: 'usuarios-nuevo-resumen',
      component: () => import('@/pages/UsersPage.vue'),
      meta: {
        section: 'USUARIOS',
        homeTo: '/usuarios/usuarios',
        pageTitle: 'NUEVO USUARIO',
        userSection: 'usuarios',
        userMode: 'create',
        userStep: 'resumen',
        breadcrumb: [{ label: 'USUARIOS', to: '/usuarios/usuarios' }, { label: 'Nuevo usuario' }, { label: 'Resumen' }],
      },
    },
    {
      path: '/usuarios/usuarios/:userId/editar/datos',
      name: 'usuarios-editar-datos',
      component: () => import('@/pages/UsersPage.vue'),
      meta: {
        section: 'USUARIOS',
        homeTo: '/usuarios/usuarios',
        pageTitle: 'EDITAR USUARIO',
        userSection: 'usuarios',
        userMode: 'edit',
        userStep: 'datos',
        breadcrumb: [{ label: 'USUARIOS', to: '/usuarios/usuarios' }, { label: 'Editar usuario' }, { label: 'Datos' }],
      },
    },
    {
      path: '/usuarios/usuarios/:userId/editar/roles',
      name: 'usuarios-editar-roles',
      component: () => import('@/pages/UsersPage.vue'),
      meta: {
        section: 'USUARIOS',
        homeTo: '/usuarios/usuarios',
        pageTitle: 'EDITAR USUARIO',
        userSection: 'usuarios',
        userMode: 'edit',
        userStep: 'roles',
        breadcrumb: [{ label: 'USUARIOS', to: '/usuarios/usuarios' }, { label: 'Editar usuario' }, { label: 'Roles' }],
      },
    },
    {
      path: '/usuarios/usuarios/:userId/editar/permisos',
      name: 'usuarios-editar-permisos',
      component: () => import('@/pages/UsersPage.vue'),
      meta: {
        section: 'USUARIOS',
        homeTo: '/usuarios/usuarios',
        pageTitle: 'EDITAR USUARIO',
        userSection: 'usuarios',
        userMode: 'edit',
        userStep: 'permisos',
        breadcrumb: [{ label: 'USUARIOS', to: '/usuarios/usuarios' }, { label: 'Editar usuario' }, { label: 'Permisos' }],
      },
    },
    {
      path: '/usuarios/usuarios/:userId/editar/resumen',
      name: 'usuarios-editar-resumen',
      component: () => import('@/pages/UsersPage.vue'),
      meta: {
        section: 'USUARIOS',
        homeTo: '/usuarios/usuarios',
        pageTitle: 'EDITAR USUARIO',
        userSection: 'usuarios',
        userMode: 'edit',
        userStep: 'resumen',
        breadcrumb: [{ label: 'USUARIOS', to: '/usuarios/usuarios' }, { label: 'Editar usuario' }, { label: 'Resumen' }],
      },
    },
    {
      path: '/usuarios/roles',
      name: 'usuarios-roles',
      component: () => import('@/pages/UsersPage.vue'),
      meta: {
        section: 'USUARIOS',
        homeTo: '/usuarios/usuarios',
        pageTitle: 'ROLES',
        userSection: 'roles',
        breadcrumb: [{ label: 'USUARIOS', to: '/usuarios/usuarios' }, { label: 'Roles' }],
      },
    },
    {
      path: '/usuarios/permisos',
      name: 'usuarios-permisos',
      component: () => import('@/pages/UsersPage.vue'),
      meta: {
        section: 'USUARIOS',
        homeTo: '/usuarios/usuarios',
        pageTitle: 'PERMISOS',
        userSection: 'permisos',
        breadcrumb: [{ label: 'USUARIOS', to: '/usuarios/usuarios' }, { label: 'Permisos' }],
      },
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach((to) => {
  const isPublicRoute = Boolean(to.meta.public)
  const isAuthenticated = hasActiveSession()

  if (!isPublicRoute && !isAuthenticated) {
    return {
      path: '/',
      query: to.fullPath !== '/' ? { redirect: to.fullPath } : undefined,
    }
  }

  if (isPublicRoute && isAuthenticated) {
    return { path: '/inicio' }
  }

  return true
})

export default router
