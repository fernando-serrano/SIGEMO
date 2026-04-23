<script setup lang="ts">
interface SidebarMenuItem {
  id: string
  label: string
  iconPath: string
  to?: string
  danger?: boolean
  active?: boolean
  action?: 'logout'
}

defineProps<{
  items: SidebarMenuItem[]
}>()

const emit = defineEmits<{
  (event: 'select', item: SidebarMenuItem): void
}>()

function onSelect(item: SidebarMenuItem): void {
  emit('select', item)
}
</script>

<template>
  <ul class="nav-list sigemo-nav-list" role="list">
    <li v-for="item in items" :key="item.id" class="sigemo-nav-item-wrap">
      <button
        type="button"
        class="nav-item"
        :class="{
          'nav-item--active': item.active,
          'sigemo-nav-item--danger': item.danger,
        }"
        @click="onSelect(item)"
      >
        <span class="nav-item__icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" class="sigemo-nav-icon" aria-hidden="true">
          <path :d="item.iconPath" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        </span>
        <span>{{ item.label }}</span>
      </button>
    </li>
  </ul>
</template>
