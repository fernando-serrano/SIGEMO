<script setup lang="ts">
import { computed } from 'vue'

import AppBrandLogo from '@/components/AppBrandLogo.vue'
import type { ThemeName } from '../types'

const props = defineProps<{ theme: ThemeName }>()

const logoVariant = computed<'dark' | 'light'>(() =>
  props.theme === 'light' || props.theme === 'corp' ? 'light' : 'dark',
)
</script>

<template>
  <section class="auth-panel auth-panel--hero" aria-label="Panel informativo">
    <div class="auth-brand">
      <div class="auth-hero-copy">
        <h1 class="auth-hero-title">
          <span class="auth-hero-title-brand" aria-label="Liderman">
          <AppBrandLogo :variant="logoVariant" />
          </span>
          <span class="auth-hero-title-text">SIGEMO</span>
        </h1>
        <p class="auth-hero-subtitle">
          Sistema de Gestion de Examenes Medicos Ocupacionales. v0.1
        </p>
      </div>
    </div>

  </section>
</template>
