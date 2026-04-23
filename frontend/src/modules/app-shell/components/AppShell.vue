<template>
  <div class="dashboard-shell">
    <slot name="sidebar" />
    <main class="dashboard-main" aria-live="polite">
      <slot />
    </main>
  </div>
</template>
