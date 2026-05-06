<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import LoginFormCard from '@/features/auth/components/LoginFormCard.vue'
import LoginHeroPanel from '@/features/auth/components/LoginHeroPanel.vue'
import LoginThemeSwitcher from '@/features/auth/components/LoginThemeSwitcher.vue'
import type { LoginUser, ThemeName } from '@/features/auth/types'
import { saveSessionUser } from '@/shared/session/session'

const router = useRouter()
const route = useRoute()
const STORAGE_KEY = 'sigemo-theme'
const allowedThemes: ThemeName[] = ['dark', 'light', 'corp', 'corp-dark']

const savedTheme = localStorage.getItem(STORAGE_KEY)
const theme = ref<ThemeName>(allowedThemes.includes(savedTheme as ThemeName) ? (savedTheme as ThemeName) : 'dark')

function applyTheme(selectedTheme: ThemeName): void {
  document.documentElement.setAttribute('data-theme', selectedTheme)
  localStorage.setItem(STORAGE_KEY, selectedTheme)
}

function onLoginSuccess(user: LoginUser): void {
  saveSessionUser(user)
  const redirect = typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/') ? route.query.redirect : '/inicio'
  void router.push(redirect)
}

onMounted(() => {
  applyTheme(theme.value)
})

watch(theme, (selectedTheme) => {
  applyTheme(selectedTheme)
})
</script>

<template>
  <main class="auth-login">
    <LoginThemeSwitcher v-model="theme" />

    <div class="auth-shell">
      <LoginHeroPanel :theme="theme" />

      <section class="auth-panel auth-panel--form" aria-label="Formulario de acceso">
        <LoginFormCard @success="onLoginSuccess" />
      </section>
    </div>
  </main>
</template>
