<script setup lang="ts">
import { computed } from 'vue'

import logoDark from '@/assets/brand/logo_liderman_dark.png'
import logoLight from '@/assets/brand/logo_liderman_light.png'

const props = withDefaults(
  defineProps<{
    variant?: 'dark' | 'light'
  }>(),
  {
    variant: 'dark',
  },
)

const brandLogo = computed(() => (props.variant === 'light' ? logoLight : logoDark))
</script>

<template>
  <img :src="brandLogo" class="auth-logo" alt="Liderman" />
</template>
