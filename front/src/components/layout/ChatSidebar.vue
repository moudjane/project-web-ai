<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getChatById, getCurrentUserChats, updateChatTitle } from '@/services/chatService'
import { useChatStore } from '@/stores/chat'

const chats = ref<Array<{ id: string; title: string }>>([])
const isLoading = ref(false)
const error = ref('')
const chatStore = useChatStore()
const editingId = ref<string | null>(null)
const editingTitle = ref('')

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

// Watch for chat store changes and refresh the list
watch(() => chatStore.getCurrentChatId, async () => {
  await loadChats()
})

const selectChat = async (chatId: string) => {
  console.log('Selected chat:', chatId)
  chatStore.setCurrentChatId(chatId)
  const chat = await getChatById(chatId)
  console.log('Chat details:', chat)
}

const startEditingTitle = (chatId: string, currentTitle: string) => {
  editingId.value = chatId
  editingTitle.value = currentTitle
}

const saveTitle = async (chatId: string) => {
  if (!editingTitle.value.trim()) {
    editingId.value = null
    return
  }

  try {
    await updateChatTitle(chatId, editingTitle.value)
    const chatIndex = chats.value.findIndex(c => c.id === chatId)
    if (chatIndex !== -1 && chats.value[chatIndex]) {
      chats.value[chatIndex]!.title = editingTitle.value
    }
    editingId.value = null
  } catch (err) {
    console.error('Failed to update chat title:', err)
  }
}

const cancelEditing = () => {
  editingId.value = null
  editingTitle.value = ''
}
</script>

<template>
  <div class="space-y-2">
    <div class="text-slate-400 text-[10px] uppercase font-bold tracking-[0.2em] px-1">Conversations</div>
    
    <div v-if="isLoading" class="text-slate-500 text-sm px-3 py-2">Chargement...</div>
    
    <div v-else-if="error" class="text-red-500 text-sm px-3 py-2">{{ error }}</div>
    
    <div v-else-if="chats.length === 0" class="text-slate-500 text-sm px-3 py-2">Aucune conversation</div>
    
    <div v-for="chat in chats" :key="chat.id" class="group relative">
      <div v-if="editingId === chat.id" class="flex gap-2 px-1">
        <input 
          v-model="editingTitle"
          type="text"
          @keyup.enter="saveTitle(chat.id)"
          @keyup.escape="cancelEditing"
          class="flex-1 min-w-0 px-2 py-1 bg-white border border-blue-500 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          autofocus
        />
        <button
          @click="saveTitle(chat.id)"
          class="flex-shrink-0 px-2 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-xs transition-colors"
          title="Enregistrer"
        >
          ✓
        </button>
        <button
          @click="cancelEditing"
          class="flex-shrink-0 px-2 py-1 bg-slate-300 hover:bg-slate-400 text-slate-700 rounded text-xs transition-colors"
          title="Annuler"
        >
          ✕
        </button>
      </div>
      <div
        v-else
        class="relative group/item py-2.5 px-3 hover:bg-slate-50 rounded-xl transition-colors border border-transparent hover:border-slate-200"
      >
        <button
          @click="selectChat(chat.id)"
          class="w-full text-left text-slate-600 text-sm font-medium cursor-pointer flex items-center gap-2 min-w-0"
        >
          <span class="flex-shrink-0">💬</span>
          <span class="truncate">{{ chat.title }}</span>
        </button>
        <button
          @click.stop="startEditingTitle(chat.id, chat.title)"
          class="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover/item:opacity-100 p-1 hover:bg-slate-200 rounded transition-all flex-shrink-0"
          title="Modifier le titre"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.8477 1.87868C19.6761 0.707109 17.7766 0.707105 16.605 1.87868L2.44744 16.0363C2.02864 16.4551 1.74317 16.9885 1.62702 17.5692L1.03995 20.5046C0.760062 21.904 1.9939 23.1379 3.39334 22.858L6.32868 22.2709C6.90945 22.1548 7.44285 21.8693 7.86165 21.4505L22.0192 7.29289C23.1908 6.12132 23.1908 4.22183 22.0192 3.05025L20.8477 1.87868ZM18.0192 3.29289C18.4098 2.90237 19.0429 2.90237 19.4335 3.29289L20.605 4.46447C20.9956 4.85499 20.9956 5.48815 20.605 5.87868L17.9334 8.55027L15.3477 5.96448L18.0192 3.29289ZM13.9334 7.3787L3.86165 17.4505C3.72205 17.5901 3.6269 17.7679 3.58818 17.9615L3.00111 20.8968L5.93645 20.3097C6.13004 20.271 6.30784 20.1759 6.44744 20.0363L16.5192 9.96448L13.9334 7.3787Z" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>