import { ref } from 'vue'
import type { FeedbackTone } from './useUserForm'

export function useToast() {
  const toastQueue = ref<Array<{ id: number; title: string; message: string; tone: FeedbackTone }>>([])
  let toastSequence = 0

  function pushToast(title: string, message: string, tone: FeedbackTone): void {
    const id = ++toastSequence
    toastQueue.value = [...toastQueue.value, { id, title, message, tone }]
    window.setTimeout(() => {
      toastQueue.value = toastQueue.value.filter((toast) => toast.id !== id)
    }, 5000)
  }

  function dismissToast(toastId: number): void {
    toastQueue.value = toastQueue.value.filter((toast) => toast.id !== toastId)
  }

  return {
    toastQueue,
    pushToast,
    dismissToast,
  }
}
