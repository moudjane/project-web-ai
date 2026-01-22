<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getChatById, getCurrentUserChats } from '@/services/chatService'
import { useChatStore } from '@/stores/chat'

const chats = ref<Array<{ id: string; title: string }>>([])
const isLoading = ref(false)
const error = ref('')
const chatStore = useChatStore()

const loadChats = async () => {
  try {
    isLoading.value = true
    error.value = ''
    chats.value = await getCurrentUserChats()
    
    if (chats.value.length > 0) {
      chatStore.setCurrentChatId(chats.value[0]?.id ?? "")
    }
    
  } catch (err) {
    console.error('Failed to load chats:', err)
    error.value = 'Failed to load chats'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadChats()
})

const selectChat = async (chatId: string) => {
  console.log('Selected chat:', chatId)
  chatStore.setCurrentChatId(chatId)
  const chat = await getChatById(chatId)
  console.log('Chat details:', chat)
}
</script>

<template>
  <div class="space-y-2">
    <div class="text-slate-400 text-[10px] uppercase font-bold tracking-[0.2em] px-1">Conversations</div>
    
    <div v-if="isLoading" class="text-slate-500 text-sm px-3 py-2">Chargement...</div>
    
    <div v-else-if="error" class="text-red-500 text-sm px-3 py-2">{{ error }}</div>
    
    <div v-else-if="chats.length === 0" class="text-slate-500 text-sm px-3 py-2">Aucune conversation</div>
    
    <button 
      v-for="chat in chats" 
      :key="chat.id"
      @click="selectChat(chat.id)"
      class="w-full text-left py-2.5 px-3 hover:bg-slate-50 rounded-xl text-slate-600 text-sm font-medium cursor-pointer transition-colors flex items-center gap-2 border border-transparent hover:border-slate-200"
    >
      <span>💬</span> {{ chat.title }}
    </button>
  </div>
</template>