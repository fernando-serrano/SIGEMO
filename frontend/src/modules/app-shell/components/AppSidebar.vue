<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppSidebarMenu from './AppSidebarMenu.vue'

interface UserSession {
  username?: string
  fullname?: string
  area?: string
}

interface SidebarItem {
  id: string
  label: string
  iconPath: string
  to?: string
  danger?: boolean
  action?: 'logout'
}

const route = useRoute()
const router = useRouter()

const quickActions: SidebarItem[] = [
  {
    id: 'users',
    label: 'Usuarios',
    iconPath: 'M16 21V19C16 17.3 14.7 16 13 16H7C5.3 16 4 17.3 4 19V21 M19 21V19C19 17.55 18.2 16.29 17 15.62 M10 12C11.93 12 13.5 10.43 13.5 8.5C13.5 6.57 11.93 5 10 5C8.07 5 6.5 6.57 6.5 8.5C6.5 10.43 8.07 12 10 12 M17 11C18.38 11 19.5 9.88 19.5 8.5C19.5 7.12 18.38 6 17 6',
  },
  {
    id: 'emos',
    label: 'EMOs',
    to: '/inicio',
    iconPath: 'M7 5H17V19H7V5 Z M10 3V7 M14 3V7 M10 12H14 M10 16H14',
  },
]

const accountActions: SidebarItem[] = [
  {
    id: 'profile',
    label: 'Mi Perfil',
    iconPath: 'M12 13C14.21 13 16 11.21 16 9C16 6.79 14.21 5 12 5C9.79 5 8 6.79 8 9C8 11.21 9.79 13 12 13 Z M5 20C5 17.24 8.13 15 12 15C15.87 15 19 17.24 19 20',
  },
  {
    id: 'settings',
    label: 'Configuracion',
    iconPath: 'M12 8.5C13.93 8.5 15.5 10.07 15.5 12C15.5 13.93 13.93 15.5 12 15.5C10.07 15.5 8.5 13.93 8.5 12C8.5 10.07 10.07 8.5 12 8.5 Z M19.4 15A1.65 1.65 0 0 0 19.73 16.82L19.79 16.88A2 2 0 1 1 16.96 19.71L16.9 19.65A1.65 1.65 0 0 0 15.08 19.32A1.65 1.65 0 0 0 14 20.84V21A2 2 0 1 1 10 21V20.84A1.65 1.65 0 0 0 8.92 19.32A1.65 1.65 0 0 0 7.1 19.65L7.04 19.71A2 2 0 1 1 4.21 16.88L4.27 16.82A1.65 1.65 0 0 0 4.6 15A1.65 1.65 0 0 0 3.08 14H3A2 2 0 1 1 3 10H3.08A1.65 1.65 0 0 0 4.6 9A1.65 1.65 0 0 0 4.27 7.18L4.21 7.12A2 2 0 1 1 7.04 4.29L7.1 4.35A1.65 1.65 0 0 0 8.92 4.68H9A1.65 1.65 0 0 0 10 3.16V3A2 2 0 1 1 14 3V3.16A1.65 1.65 0 0 0 15.08 4.68H15.16A1.65 1.65 0 0 0 16.9 4.35L16.96 4.29A2 2 0 1 1 19.79 7.12L19.73 7.18A1.65 1.65 0 0 0 19.4 9V9.08A1.65 1.65 0 0 0 20.92 10H21A2 2 0 1 1 21 14H20.92A1.65 1.65 0 0 0 19.4 15Z',
  },
  {
    id: 'logout',
    label: 'Cerrar Sesion',
    action: 'logout' as const,
    danger: true,
    iconPath: 'M9 21H5C4.45 21 4 20.55 4 20V4C4 3.45 4.45 3 5 3H9 M16 17L21 12L16 7 M21 12H9',
  },
]

const userSession = computed<UserSession>(() => {
  const raw = sessionStorage.getItem('sigemo-user')

  if (!raw) {
    return { username: 'usuario', fullname: 'Usuario SIGEMO' }
  }

  try {
    return JSON.parse(raw) as UserSession
  } catch {
    return { username: 'usuario', fullname: 'Usuario SIGEMO' }
  }
})

const mainMenu = computed(() =>
  quickActions.map((item) => ({
    ...item,
    active: Boolean(item.to && route.path.startsWith(item.to)),
  })),
)

const footerMenu = computed(() =>
  accountActions.map((item) => ({
    ...item,
    active: Boolean(item.to && route.path.startsWith(item.to)),
  })),
)

const userInitials = computed(() => {
  const source = userSession.value.fullname || userSession.value.username || 'US'

  return source
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase())
    .join('')
    .slice(0, 2)
})

function onSelectItem(item: { to?: string; action?: 'logout' }): void {
  if (item.action === 'logout') {
    sessionStorage.removeItem('sigemo-user')
    void router.push('/')
    return
  }

  if (!item.to || item.to === '/inicio' || item.to === route.path) {
    return
  }

  void router.push(item.to)
}
</script>

<template>
  <aside class="sidebar sidebar--acrylic sigemo-sidebar" aria-label="Navegacion lateral">
    <section class="sidebar__header sigemo-sidebar-brand">
      <span class="avatar avatar--sm sigemo-brand-avatar" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" class="sigemo-brand-avatar-icon">
          <rect x="4" y="4" width="16" height="16" stroke="currentColor" stroke-width="1.8" />
          <path d="M12 8V16 M8 12H16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
        </svg>
      </span>
      <div>
        <p class="sidebar__title">SIGEMO</p>
      </div>
    </section>

    <section class="section-header section-header--flush sigemo-sidebar-section">
      <p class="section-header__title">Modulos</p>
    </section>
    <AppSidebarMenu :items="mainMenu" @select="onSelectItem" />

    <div class="sigemo-sidebar-spacer" />

    <section class="section-header section-header--flush sigemo-sidebar-section">
      <p class="section-header__title">Cuenta</p>
    </section>
    <AppSidebarMenu :items="footerMenu" @select="onSelectItem" />

    <section class="sidebar__footer sigemo-sidebar-user" aria-label="Usuario activo">
      <span class="avatar avatar--sm avatar--ring">
        <span class="avatar__initials">{{ userInitials }}</span>
      </span>
      <div class="sigemo-sidebar-user-meta">
        <p class="sigemo-sidebar-user-name">{{ userSession.fullname || 'Usuario SIGEMO' }}</p>
        <p class="sigemo-sidebar-user-id">{{ userSession.username || 'usuario' }}</p>
      </div>
    </section>
  </aside>
</template>
