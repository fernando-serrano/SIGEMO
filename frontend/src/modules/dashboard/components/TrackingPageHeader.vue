<script setup lang="ts">
defineProps<{
  section: string
  pageTitle: string
}>()
</script>

<template>
  <header class="tracking-heading">
    <nav class="breadcrumb breadcrumb--slash" aria-label="Breadcrumb">
      <ol class="breadcrumb__list">
        <li class="breadcrumb__item">
          <span class="breadcrumb__link tracking-breadcrumb-home">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M3 11L12 4L21 11 M6 9.5V19H18V9.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
        </li>
        <li class="breadcrumb__item">
          <span class="breadcrumb__link">{{ section }}</span>
        </li>
        <li class="breadcrumb__item breadcrumb__item--active" aria-current="page">{{ pageTitle }}</li>
      </ol>
    </nav>

    <h1 class="tracking-title">
      {{ pageTitle }}
      <span aria-hidden="true" class="tracking-title-accent" />
    </h1>
  </header>
</template>
