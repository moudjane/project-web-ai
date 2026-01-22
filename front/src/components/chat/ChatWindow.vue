<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { chatWithMistral, type ChatMessage } from '@/services/mistralService'
import { createChat, savePrompt, getChatHistory, queryVectorStore } from '@/services/chatService'
import { useChatStore } from '@/stores/chat'

const prompt = ref('')
const messages = ref<ChatMessage[]>([])
const isLoading = ref(false)
const chatStore = useChatStore()
let currentChatId: string | null = null

const loadChatHistory = async () => {
  if (!currentChatId) return
  
  try {
    const history = await getChatHistory(currentChatId)
    console.log('Loaded chat history:', history)
    
    // Map the history to ChatMessage format
    messages.value = history.map((doc) => ({
      role: doc.role as 'user' | 'assistant',
      content: doc.content as string
    }))
    
    console.log('Mapped messages:', messages.value)
  } catch (error) {
    console.error('Failed to load chat history:', error)
  }
}

onMounted(async () => {
  currentChatId = chatStore.getCurrentChatId
  await loadChatHistory()
})

watch(() => chatStore.getCurrentChatId, async (newChatId) => {
  currentChatId = newChatId
  await loadChatHistory()
})

const handleSendPrompt = async () => {
  if (!prompt.value.trim()) return

  if (!currentChatId) {
    currentChatId = await createChat("Nouveau Chat", "Révisions")
    chatStore.setCurrentChatId(currentChatId)
  }

  const promptText = prompt.value
  const userMessage: ChatMessage = {
    role: 'user',
    content: promptText,
  }
  
  messages.value.push(userMessage)
  prompt.value = ''
  isLoading.value = true

  try {
    // 1. Sauvegarder la question utilisateur dans Firestore
    await savePrompt(currentChatId, promptText)

    // 2. RAG : Chercher du contexte dans les PDF via le backend Python
    const context = await queryVectorStore(promptText)
    
    // 3. Préparer les messages pour Mistral (avec contexte si disponible)
    const conversationForMistral = [...messages.value]
    
    if (context) {
      const augmentedContent = `Utilise uniquement les informations suivantes pour répondre à la question de l'utilisateur. Si tu ne trouves pas la réponse dans le contexte, dis-le poliment.

CONTEXTE :
${context}

QUESTION :
${promptText}`

      // On remplace le contenu du dernier message pour l'API Mistral uniquement
      conversationForMistral[conversationForMistral.length - 1] = {
        role: 'user',
        content: augmentedContent
      }
    }

    // 4. Obtenir la réponse de Mistral
    const response = await chatWithMistral(conversationForMistral)

    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: response,
    }
    messages.value.push(assistantMessage)
    
    // 5. Sauvegarder la réponse de l'assistant
    await savePrompt(currentChatId, response, 'assistant')
  } catch (error) {
    console.error('Failed to process message:', error)
    // Optionnel : ajouter un message d'erreur dans l'interface
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="flex-1 flex flex-col h-full bg-slate-50 text-slate-900">
    <div class="flex-1 overflow-y-auto p-8 space-y-4">
      <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center">
        <div class="w-16 h-16 bg-blue-600/15 rounded-full flex items-center justify-center mb-4">
          <span class="text-2xl">🤖</span>
        </div>
        <h2 class="text-2xl font-semibold">Prêt à réviser ?</h2>
        <p class="text-slate-600 mt-2">Pose une question sur tes documents indexés.</p>
      </div>

      <div v-for="(message, index) in messages" :key="index" class="flex gap-4" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
        <div v-if="message.role === 'assistant'" class="flex-shrink-0 w-8 h-8 bg-blue-600/15 rounded-full flex items-center justify-center">
          <span class="text-sm">🤖</span>
        </div>
        <div
          class="max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg"
          :class="message.role === 'user'
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-slate-200 text-slate-900 rounded-bl-none'"
        >
          <p class="text-sm">{{ message.content }}</p>
        </div>
        <div v-if="message.role === 'user'" class="flex-shrink-0 w-8 h-8 bg-slate-300 rounded-full flex items-center justify-center">
          <span class="text-sm">👤</span>
        </div>
      </div>

      <div v-if="isLoading" class="flex gap-4">
        <div class="flex-shrink-0 w-8 h-8 bg-blue-600/15 rounded-full flex items-center justify-center">
          <span class="text-sm">🤖</span>
        </div>
        <div class="bg-slate-200 text-slate-900 px-4 py-3 rounded-lg rounded-bl-none">
          <div class="flex gap-2">
            <div class="w-2 h-2 bg-slate-500 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
            <div class="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="p-6 border-t border-slate-200 bg-white/90 backdrop-blur-sm">
      <div class="flex items-center gap-4 w-full">
        <input 
          v-model="prompt"
          type="text"
          placeholder="Ecris ton message ici..."
          :disabled="isLoading"
          @keyup.enter="handleSendPrompt"
          class="flex-1 bg-white border border-slate-200 text-slate-900 rounded-lg py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all placeholder:text-slate-500 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button 
          @click="handleSendPrompt"
          :disabled="isLoading || !prompt.trim()"
          class="flex-shrink-0 p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>