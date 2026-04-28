<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import type { ThemeName } from '@/features/auth/types'
import AppBrandLogo from '@/shared/components/AppBrandLogo.vue'
import AppSidebarMenu from './AppSidebarMenu.vue'

interface UserSession {
  username?: string
  name?: string
  last_name?: string
  fullname?: string
  area?: string
  role_name?: string
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
const THEME_STORAGE_KEY = 'sigemo-theme'
const allowedThemes: ThemeName[] = ['dark', 'light', 'corp', 'corp-dark']

const savedTheme = localStorage.getItem(THEME_STORAGE_KEY)
const theme = ref<ThemeName>(
  allowedThemes.includes(savedTheme as ThemeName) ? (savedTheme as ThemeName) : 'dark',
)

const emit = defineEmits<{
  (event: 'close'): void
}>()

const quickActions: SidebarItem[] = [
  {
    id: 'users',
    label: 'Usuarios',
    to: '/usuarios',
    iconPath: 'M16 21V19C16 17.3 14.7 16 13 16H7C5.3 16 4 17.3 4 19V21 M19 21V19C19 17.55 18.2 16.29 17 15.62 M10 12C11.93 12 13.5 10.43 13.5 8.5C13.5 6.57 11.93 5 10 5C8.07 5 6.5 6.57 6.5 8.5C6.5 10.43 8.07 12 10 12 M17 11C18.38 11 19.5 9.88 19.5 8.5C19.5 7.12 18.38 6 17 6',
  },
  {
    id: 'emos',
    label: 'EMOs',
    to: '/inicio',
    iconPath: 'M7 5H17V19H7V5 Z M10 3V7 M14 3V7 M10 12H14 M10 16H14',
  },
]

const logoutAction: SidebarItem = {
  id: 'logout',
  label: 'Cerrar Sesion',
  action: 'logout',
  danger: true,
  iconPath: 'M9 21H5C4.45 21 4 20.55 4 20V4C4 3.45 4.45 3 5 3H9 M16 17L21 12L16 7 M21 12H9',
}

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

const userInitials = computed(() => {
  const firstName = userSession.value.name?.trim().split(/\s+/).find(Boolean)?.charAt(0).toUpperCase()
  const firstLastName = userSession.value.last_name?.trim().split(/\s+/).find(Boolean)?.charAt(0).toUpperCase()

  if (firstName || firstLastName) {
    return `${firstName ?? ''}${firstLastName ?? ''}` || 'US'
  }

  const source = userSession.value.fullname || userSession.value.username || 'US'
  return source
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase())
    .join('')
    .slice(0, 2)
})

const userRoleLabel = computed(() => {
  const roleName = userSession.value.role_name?.trim()

  if (roleName) {
    return roleName
  }

  return userSession.value.username || 'usuario'
})

function onSelectItem(item: { to?: string; action?: 'logout' }): void {
  if (item.action === 'logout') {
    sessionStorage.removeItem('sigemo-user')
    emit('close')
    void router.push('/')
    return
  }

  if (!item.to || item.to === '/inicio' || item.to === route.path) {
    emit('close')
    return
  }

  emit('close')
  void router.push(item.to)
}

function applyTheme(selectedTheme: ThemeName): void {
  document.documentElement.setAttribute('data-theme', selectedTheme)
  localStorage.setItem(THEME_STORAGE_KEY, selectedTheme)
}

function cycleTheme(): void {
  const currentIndex = allowedThemes.indexOf(theme.value)
  const nextIndex = currentIndex === -1 ? 0 : (currentIndex + 1) % allowedThemes.length
  theme.value = allowedThemes[nextIndex] ?? 'dark'
}

const currentThemeKind = computed<'light' | 'dark' | 'corp' | 'corp-dark'>(() => {
  switch (theme.value) {
    case 'dark':
      return 'light'
    case 'corp-dark':
      return 'dark'
    case 'light':
      return 'corp'
    default:
      return 'corp-dark'
  }
})

const logoVariant = computed<'dark' | 'light'>(() =>
  theme.value === 'light' || theme.value === 'corp' ? 'light' : 'dark',
)

applyTheme(theme.value)

watch(theme, (selectedTheme) => {
  applyTheme(selectedTheme)
})
</script>

<template>
  <aside class="sidebar sidebar--acrylic sigemo-sidebar" aria-label="Navegacion lateral">
    <section class="sidebar__header sigemo-sidebar-brand">
      <div class="sigemo-sidebar-brand-main">
        <div>
          <p class="sidebar__title sigemo-sidebar-logo-wrap">
            <AppBrandLogo :variant="logoVariant" class="sigemo-sidebar-logo" />
          </p>
          <p class="glow-text--strong sigemo-sidebar-system-name">SIGEMO</p>
        </div>
      </div>

      <button
        type="button"
        class="icon-btn icon-btn--ghost sigemo-sidebar-close"
        aria-label="Cerrar menu lateral"
        @click="emit('close')"
      >
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M6 6L18 18 M18 6L6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
        </svg>
      </button>
    </section>

    <section class="section-header section-header--flush sigemo-sidebar-section">
      <p class="section-header__title">Modulos</p>
    </section>
    <AppSidebarMenu :items="mainMenu" @select="onSelectItem" />

    <div class="sigemo-sidebar-spacer" />

    <section class="sidebar__footer sigemo-account-panel" aria-label="Usuario activo">
      <div class="sigemo-sidebar-user">
        <span class="avatar avatar--sm avatar--ring">
          <span class="avatar__initials">{{ userInitials }}</span>
        </span>
        <span class="sigemo-sidebar-user-meta">
          <span class="sigemo-sidebar-user-name">{{ userSession.fullname || 'Usuario SIGEMO' }}</span>
          <span class="glow-text--strong sigemo-sidebar-user-role">{{ userRoleLabel }}</span>
        </span>
        <button
          type="button"
          class="icon-btn icon-btn--ghost sigemo-theme-icon"
          :data-theme-kind="currentThemeKind"
          aria-label="Cambiar estilo visual"
          @click="cycleTheme"
        >
          <svg
            v-if="currentThemeKind === 'light'"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            aria-hidden="true"
          >
            <circle cx="8" cy="8" r="3" />
            <line x1="8" y1="0.5" x2="8" y2="2.5" />
            <line x1="8" y1="13.5" x2="8" y2="15.5" />
            <line x1="0.5" y1="8" x2="2.5" y2="8" />
            <line x1="13.5" y1="8" x2="15.5" y2="8" />
            <line x1="2.7" y1="2.7" x2="4.1" y2="4.1" />
            <line x1="11.9" y1="11.9" x2="13.3" y2="13.3" />
            <line x1="2.7" y1="13.3" x2="4.1" y2="11.9" />
            <line x1="11.9" y1="4.1" x2="13.3" y2="2.7" />
          </svg>
          <svg
            v-else-if="currentThemeKind === 'corp'"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <rect x="1" y="5" width="14" height="10" rx="1" />
            <path d="M5 5V3.5A1.5 1.5 0 0 1 6.5 2h3A1.5 1.5 0 0 1 11 3.5V5" />
            <line x1="1" y1="10" x2="15" y2="10" />
          </svg>
          <svg
            v-else-if="currentThemeKind === 'corp-dark'"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <rect x="1" y="5" width="14" height="10" rx="1" />
            <path d="M5 5V3.5A1.5 1.5 0 0 1 6.5 2h3A1.5 1.5 0 0 1 11 3.5V5" />
            <line x1="1" y1="10" x2="15" y2="10" />
            <circle cx="8" cy="10" r="1.5" fill="currentColor" />
          </svg>
          <svg
            v-else
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M14 9.5A6.5 6.5 0 0 1 6.5 2 6.5 6.5 0 1 0 14 9.5z" />
          </svg>
        </button>
      </div>

      <div class="sigemo-account-logout">
        <AppSidebarMenu :items="[logoutAction]" @select="onSelectItem" />
      </div>
    </section>
  </aside>
</template>
