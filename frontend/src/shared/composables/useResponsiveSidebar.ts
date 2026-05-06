import { onBeforeUnmount, onMounted, ref } from 'vue'

export function useResponsiveSidebar(mediaQuery = '(max-width: 1080px)') {
  const isSidebarOpen = ref(false)
  const breakpoint = window.matchMedia(mediaQuery)

  function openSidebar(): void {
    isSidebarOpen.value = true
  }

  function closeSidebar(): void {
    isSidebarOpen.value = false
  }

  function handleViewportChange(event: MediaQueryListEvent): void {
    if (!event.matches) {
      closeSidebar()
    }
  }

  onMounted(() => {
    if (breakpoint.matches) {
      closeSidebar()
    }

    breakpoint.addEventListener('change', handleViewportChange)
  })

  onBeforeUnmount(() => {
    breakpoint.removeEventListener('change', handleViewportChange)
  })

  return {
    isSidebarOpen,
    openSidebar,
    closeSidebar,
  }
}
