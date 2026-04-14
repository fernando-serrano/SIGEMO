<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = computed(() => {
  const raw = sessionStorage.getItem('sigemo-user')

  if (!raw) {
    return 'usuario'
  }

  try {
    const parsed = JSON.parse(raw) as { username?: string }
    return parsed.username || 'usuario'
  } catch {
    return 'usuario'
  }
})

function logout(): void {
  sessionStorage.removeItem('sigemo-user')
  void router.push('/')
}
</script>

<template>
  <main class="auth-dashboard">
    <section class="card card--acrylic auth-dashboard-card">
      <p class="auth-kicker">SIGEMO</p>
      <h1 class="auth-login-title">Inicio</h1>
      <p class="auth-login-copy">Sesion activa: {{ username }}</p>
      <button type="button" class="btn btn--secondary" @click="logout">Cerrar sesion</button>
    </section>
  </main>
</template>
