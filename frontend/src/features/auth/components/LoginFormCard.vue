<script setup lang="ts">
import { computed, ref } from 'vue'

import { login } from '../api/auth.api'
import type { LoginUser } from '../types'

const emit = defineEmits<{
  (event: 'success', user: LoginUser): void
}>()

const username = ref('')
const password = ref('')
const isSubmitting = ref(false)
const showPassword = ref(false)
const statusMessage = ref('')
const statusType = ref<'error' | 'success' | null>(null)

const passwordInputType = computed(() => (showPassword.value ? 'text' : 'password'))

function setStatus(message: string, type: 'error' | 'success' | null = null): void {
  statusMessage.value = message
  statusType.value = type
}

async function handleSubmit(event: Event): Promise<void> {
  event.preventDefault()

  if (!username.value.trim() || !password.value) {
    setStatus('Completa usuario y contrasena', 'error')
    return
  }

  isSubmitting.value = true
  setStatus('Validando credenciales...')

  try {
    const user = await login({
      username: username.value.trim(),
      password: password.value,
    })

    setStatus(`Bienvenido, ${user.username}`, 'success')
    emit('success', user)
  } catch (error) {
    const message = error instanceof Error ? error.message : 'No se pudo iniciar sesion'
    setStatus(message, 'error')
  } finally {
    isSubmitting.value = false
  }
}

function togglePasswordVisibility(): void {
  showPassword.value = !showPassword.value
}
</script>

<template>
  <section class="card card--acrylic card--elevated auth-login-card">
    <div class="auth-login-content">
      <p class="auth-kicker">Hola!</p>
      <h2 class="auth-login-title">Bienvenido de nuevo</h2>
      <p class="auth-login-copy">Ingresa con tu usuario y contrasena asignados.</p>

      <form class="auth-form" @submit="handleSubmit">
        <div class="auth-field-group">
          <label class="input-label auth-input-label" for="username">
            <span class="auth-label-icon" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 12C14.2091 12 16 10.2091 16 8C16 5.79086 14.2091 4 12 4C9.79086 4 8 5.79086 8 8C8 10.2091 9.79086 12 12 12Z" stroke="currentColor" stroke-width="1.8" />
                <path d="M5 20C5 17.2386 8.13401 15 12 15C15.866 15 19 17.2386 19 20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
              </svg>
            </span>
            Usuario
          </label>
          <input
            id="username"
            v-model="username"
            name="username"
            class="input"
            type="text"
            autocomplete="username"
            placeholder="usuario"
            required
          />
        </div>

        <div class="auth-field-group">
          <label class="input-label auth-input-label" for="password">
            <span class="auth-label-icon" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="5" y="11" width="14" height="9" rx="2" stroke="currentColor" stroke-width="1.8" />
                <path d="M8 11V8.5C8 6.567 9.567 5 11.5 5H12.5C14.433 5 16 6.567 16 8.5V11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
              </svg>
            </span>
            Contrasena
          </label>

          <div class="input-group input-group--has-icon-end auth-password-group">
            <input
              id="password"
              v-model="password"
              name="password"
              class="input"
              :type="passwordInputType"
              autocomplete="current-password"
              placeholder="Ingresa tu clave"
              required
            />

            <button
              type="button"
              class="auth-visibility-toggle"
              :aria-label="showPassword ? 'Ocultar contrasena' : 'Mostrar contrasena'"
              :aria-pressed="showPassword"
              @click="togglePasswordVisibility"
            >
              <span v-if="!showPassword">Mostrar</span>
              <span v-else>Ocultar</span>
            </button>
          </div>
        </div>

        <button type="submit" class="btn btn--primary auth-submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Validando...' : 'Iniciar sesion' }}
        </button>

        <p
          class="auth-status"
          :class="{
            'auth-status--error': statusType === 'error',
            'auth-status--success': statusType === 'success',
          }"
          aria-live="polite"
        >
          {{ statusMessage }}
        </p>
      </form>

      <p class="auth-legal">© 2026 Liderman. Todos los derechos reservados.</p>
    </div>
  </section>
</template>
