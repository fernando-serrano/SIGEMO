<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import LoginFormCard from '@/modules/auth/components/LoginFormCard.vue'
import LoginHeroPanel from '@/modules/auth/components/LoginHeroPanel.vue'
import LoginThemeSwitcher from '@/modules/auth/components/LoginThemeSwitcher.vue'
import type { LoginUser, ThemeName } from '@/modules/auth/types'

const router = useRouter()
const STORAGE_KEY = 'sigemo-theme'
const allowedThemes: ThemeName[] = ['dark', 'light', 'corp', 'corp-dark']

const savedTheme = localStorage.getItem(STORAGE_KEY)
const theme = ref<ThemeName>(allowedThemes.includes(savedTheme as ThemeName) ? (savedTheme as ThemeName) : 'dark')

function applyTheme(selectedTheme: ThemeName): void {
  document.documentElement.setAttribute('data-theme', selectedTheme)
  localStorage.setItem(STORAGE_KEY, selectedTheme)
}

function onLoginSuccess(user: LoginUser): void {
  sessionStorage.setItem('sigemo-user', JSON.stringify(user))
  void router.push('/inicio')
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
