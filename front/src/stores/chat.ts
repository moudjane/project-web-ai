import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', () => {
  const chatId = ref<string | null>(null)

  const setCurrentChatId = (id: string) => {
    chatId.value = id
  }

  const getCurrentChatId = computed(() => chatId.value)

  return {
    chatId,
    setCurrentChatId,
    getCurrentChatId
  }
})
