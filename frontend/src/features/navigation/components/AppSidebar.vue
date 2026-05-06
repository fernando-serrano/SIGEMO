<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import type { ThemeName } from '@/features/auth/types'
import AppBrandLogo from '@/shared/components/AppBrandLogo.vue'
import { clearSession, readSessionUser } from '@/shared/session/session'
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

const sucamecItems: SidebarItem[] = [
  {
    id: 'sucamec-dashboard',
    label: 'Panel',
    to: '/sucamec',
    iconPath: 'M4 13H9V20H4V13 Z M10.5 4H19.5V11H10.5V4 Z M10.5 13H19.5V20H10.5V13 Z M4 4H9V11H4V4 Z',
  },
  {
    id: 'sucamec-card-status',
    label: 'Estados',
    to: '/sucamec/estados-carne',
    iconPath: 'M8 9H16C17.1 9 18 9.9 18 11V17C18 18.1 17.1 19 16 19H8C6.9 19 6 18.1 6 17V11C6 9.9 6.9 9 8 9Z M9 13H9.01 M15 13H15.01 M10 16H14 M12 9V5 M9 5H15 M5 13H3 M21 13H19',
  },
]

const sigemoItems: SidebarItem[] = [
  {
    id: 'emos',
    label: 'EMOs',
    to: '/inicio',
    iconPath: 'M10 4.75H14V10H19.25V14H14V19.25H10V14H4.75V10H10V4.75Z',
  },
]

const usersItems: SidebarItem[] = [
  {
    id: 'users-list',
    label: 'Usuarios',
    to: '/usuarios/usuarios',
    iconPath: 'M16 21V19C16 17.3 14.7 16 13 16H7C5.3 16 4 17.3 4 19V21 M19 21V19C19 17.55 18.2 16.29 17 15.62 M10 12C11.93 12 13.5 10.43 13.5 8.5C13.5 6.57 11.93 5 10 5C8.07 5 6.5 6.57 6.5 8.5C6.5 10.43 8.07 12 10 12 M17 11C18.38 11 19.5 9.88 19.5 8.5C19.5 7.12 18.38 6 17 6',
  },
  {
    id: 'users-roles',
    label: 'Roles',
    to: '/usuarios/roles',
    iconPath: 'M12 14C14.7614 14 17 11.7614 17 9C17 6.23858 14.7614 4 12 4C9.23858 4 7 6.23858 7 9C7 11.7614 9.23858 14 12 14Z M4 20C4.8 17.6 7.1 16 9.8 16H14.2C16.9 16 19.2 17.6 20 20 M12 1.5V3.5 M4.9 4.9L6.3 6.3 M19.1 4.9L17.7 6.3',
  },
  {
    id: 'users-permissions',
    label: 'Permisos',
    to: '/usuarios/permisos',
    iconPath: 'M16 21V19C16 17.3 14.7 16 13 16H7C5.3 16 4 17.3 4 19V21 M19 21V19C19 17.55 18.2 16.29 17 15.62 M10 12C11.93 12 13.5 10.43 13.5 8.5C13.5 6.57 11.93 5 10 5C8.07 5 6.5 6.57 6.5 8.5C6.5 10.43 8.07 12 10 12 M17 11C18.38 11 19.5 9.88 19.5 8.5C19.5 7.12 18.38 6 17 6',
  },
]

const isSucamecExpanded = ref(false)
const isSigemoExpanded = ref(false)
const isUsersExpanded = ref(false)

const logoutAction: SidebarItem = {
  id: 'logout',
  label: 'Cerrar Sesion',
  action: 'logout',
  danger: true,
  iconPath: 'M9 21H5C4.45 21 4 20.55 4 20V4C4 3.45 4.45 3 5 3H9 M16 17L21 12L16 7 M21 12H9',
}

const userSession = computed<UserSession>(() => {
  return readSessionUser<UserSession>() ?? { username: 'usuario', fullname: 'Usuario MGA GADSO' }
})

const sigemoMenu = computed(() =>
  sigemoItems.map((item) => ({
    ...item,
    active: Boolean(item.to && route.path.startsWith(item.to)),
  })),
)

const sucamecMenu = computed(() =>
  sucamecItems.map((item) => ({
    ...item,
    active: Boolean(item.to && (item.to === '/sucamec' ? route.path === item.to : route.path.startsWith(item.to))),
  })),
)

const usersMenu = computed(() =>
  usersItems.map((item) => ({
    ...item,
    active: Boolean(item.to && route.path.startsWith(item.to)),
  })),
)

const isSucamecActive = computed(() => sucamecMenu.value.some((item) => item.active))
const isSigemoActive = computed(() => sigemoMenu.value.some((item) => item.active))
const isUsersActive = computed(() => usersMenu.value.some((item) => item.active))

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
    clearSession()
    emit('close')
    void router.push('/')
    return
  }

  if (!item.to || item.to === route.path) {
    emit('close')
    return
  }

  emit('close')
  void router.push(item.to)
}

function toggleSigemoModule(): void {
  isSigemoExpanded.value = !isSigemoExpanded.value
}

function toggleSucamecModule(): void {
  isSucamecExpanded.value = !isSucamecExpanded.value
}

function toggleUsersModule(): void {
  isUsersExpanded.value = !isUsersExpanded.value
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
          <p class="glow-text--strong sigemo-sidebar-system-name">MGA GADSO</p>
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
    <section class="sigemo-module-group" aria-label="Modulo Usuarios">
      <button
        type="button"
        class="nav-item sigemo-module-trigger"
        :class="{ 'nav-item--active': isUsersActive }"
        :aria-expanded="isUsersExpanded"
        @click="toggleUsersModule"
      >
        <span class="nav-item__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" class="sigemo-nav-icon" aria-hidden="true">
            <path
              d="M12 12C14.2091 12 16 10.2091 16 8C16 5.79086 14.2091 4 12 4C9.79086 4 8 5.79086 8 8C8 10.2091 9.79086 12 12 12Z M5 20C5 17.2386 8.13401 15 12 15C15.866 15 19 17.2386 19 20"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span class="sigemo-module-trigger-label">USUARIOS</span>
        <span class="sigemo-module-trigger-chevron" :data-expanded="isUsersExpanded" aria-hidden="true">
          <svg viewBox="0 0 16 16" fill="none">
            <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </span>
      </button>

      <div v-show="isUsersExpanded" class="sigemo-module-children">
        <AppSidebarMenu :items="usersMenu" @select="onSelectItem" />
      </div>
    </section>

    <section class="sigemo-module-group" aria-label="Modulo SUCAMEC">
      <button
        type="button"
        class="nav-item sigemo-module-trigger"
        :class="{ 'nav-item--active': isSucamecActive }"
        :aria-expanded="isSucamecExpanded"
        @click="toggleSucamecModule"
      >
        <span class="nav-item__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" class="sigemo-nav-icon" aria-hidden="true">
            <path
              d="M12 3L19 6V11C19 15.97 15.82 20.46 12 21C8.18 20.46 5 15.97 5 11V6L12 3Z"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span class="sigemo-module-trigger-label">SUCAMEC</span>
        <span class="sigemo-module-trigger-chevron" :data-expanded="isSucamecExpanded" aria-hidden="true">
          <svg viewBox="0 0 16 16" fill="none">
            <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </span>
      </button>

      <div v-show="isSucamecExpanded" class="sigemo-module-children">
        <AppSidebarMenu :items="sucamecMenu" @select="onSelectItem" />
      </div>
    </section>

    <section class="sigemo-module-group" aria-label="Modulo SIGEMO">
      <button
        type="button"
        class="nav-item sigemo-module-trigger"
        :class="{ 'nav-item--active': isSigemoActive }"
        :aria-expanded="isSigemoExpanded"
        @click="toggleSigemoModule"
      >
        <span class="nav-item__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" class="sigemo-nav-icon" aria-hidden="true">
            <path
              d="M10 4.75H14V10H19.25V14H14V19.25H10V14H4.75V10H10V4.75Z"
              stroke="currentColor"
              stroke-width="1.9"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span class="sigemo-module-trigger-label">SIGEMO</span>
        <span class="sigemo-module-trigger-chevron" :data-expanded="isSigemoExpanded" aria-hidden="true">
          <svg viewBox="0 0 16 16" fill="none">
            <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </span>
      </button>

      <div v-show="isSigemoExpanded" class="sigemo-module-children">
        <AppSidebarMenu :items="sigemoMenu" @select="onSelectItem" />
      </div>
    </section>

    <div class="sigemo-sidebar-spacer" />

    <section class="sidebar__footer sigemo-account-panel" aria-label="Usuario activo">
      <div class="sigemo-sidebar-user">
        <span class="avatar avatar--sm avatar--ring">
          <span class="avatar__initials">{{ userInitials }}</span>
        </span>
        <span class="sigemo-sidebar-user-meta">
          <span class="sigemo-sidebar-user-name">{{ userSession.fullname || 'Usuario MGA GADSO' }}</span>
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
