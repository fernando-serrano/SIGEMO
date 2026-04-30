<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface BreadcrumbItem {
  label: string
  to?: string
}

const props = defineProps<{
  section?: string
  pageTitle?: string
  breadcrumb?: BreadcrumbItem[]
}>()

const route = useRoute()

const routeSection = computed(() => String(route.meta.section ?? '').trim())
const routePageTitle = computed(() => String(route.meta.pageTitle ?? '').trim())
const routeHomeTo = computed(() => String(route.meta.homeTo ?? '/inicio').trim() || '/inicio')
const routeBreadcrumb = computed<BreadcrumbItem[]>(() => {
  if (!Array.isArray(route.meta.breadcrumb)) {
    return []
  }

  return route.meta.breadcrumb
    .map((item) => {
      if (typeof item === 'string') {
        return { label: item.trim() }
      }

      if (item && typeof item === 'object' && 'label' in item) {
        return {
          label: String(item.label ?? '').trim(),
          to: typeof item.to === 'string' ? item.to.trim() : undefined,
        }
      }

      return null
    })
    .filter((item): item is BreadcrumbItem => Boolean(item?.label))
})

const resolvedSection = computed(() => props.section?.trim() || routeSection.value)
const resolvedPageTitle = computed(() => props.pageTitle?.trim() || routePageTitle.value)
const resolvedBreadcrumb = computed<BreadcrumbItem[]>(() => {
  if (props.breadcrumb?.length) {
    return props.breadcrumb
  }

  if (routeBreadcrumb.value.length > 0) {
    return routeBreadcrumb.value
  }

  return [resolvedSection.value, resolvedPageTitle.value]
    .filter(Boolean)
    .map((item) => ({ label: item }))
})
</script>

<template>
  <header class="tracking-heading">
    <nav class="breadcrumb breadcrumb--slash" aria-label="Breadcrumb">
      <ol class="breadcrumb__list">
        <li class="breadcrumb__item">
          <RouterLink :to="routeHomeTo" class="breadcrumb__link tracking-breadcrumb-home" aria-label="Ir a inicio">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M3 11L12 4L21 11 M6 9.5V19H18V9.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </RouterLink>
        </li>
        <li
          v-for="(item, index) in resolvedBreadcrumb"
          :key="`${item.label}-${index}`"
          class="breadcrumb__item"
          :class="{ 'breadcrumb__item--active': index === resolvedBreadcrumb.length - 1 }"
          :aria-current="index === resolvedBreadcrumb.length - 1 ? 'page' : undefined"
        >
          <RouterLink
            v-if="item.to && index !== resolvedBreadcrumb.length - 1"
            :to="item.to"
            class="breadcrumb__link"
          >
            {{ item.label }}
          </RouterLink>
          <span v-else class="breadcrumb__link">{{ item.label }}</span>
        </li>
      </ol>
    </nav>

    <h1 class="tracking-title">
      {{ resolvedPageTitle }}
      <span aria-hidden="true" class="tracking-title-accent" />
    </h1>
  </header>
</template>
