<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { chatWithMistralStream, type ChatMessage } from '@/services/mistralService'
import { createChat, savePrompt, getChatHistory, queryVectorStore } from '@/services/chatService'
import { useChatStore } from '@/stores/chat'
import { marked } from 'marked' // 1. Import de marked

const prompt = ref('')
const messages = ref<ChatMessage[]>([])
const isLoading = ref(false)
const chatStore = useChatStore()
let currentChatId: string | null = null
const chatContainer = ref<HTMLElement | null>(null)

marked.setOptions({
  breaks: true,
  gfm: true,
})

const renderMarkdown = (text: string) => {
  return marked.parse(text)
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const loadChatHistory = async () => {
  if (!currentChatId) return

  try {
    const history = await getChatHistory(currentChatId)
    messages.value = history.map((doc) => ({
      role: doc.role as 'user' | 'assistant',
      content: doc.content as string,
    }))
  } catch (error) {
    console.error('Failed to load chat history:', error)
  }
}

onMounted(async () => {
  currentChatId = chatStore.getCurrentChatId
  await loadChatHistory()
})

watch(
  () => chatStore.getCurrentChatId,
  async (newChatId) => {
    currentChatId = newChatId
    await loadChatHistory()
  },
)

const handleSendPrompt = async () => {
  if (!prompt.value.trim()) return

  if (!currentChatId) {
    currentChatId = await createChat('Nouveau Chat', 'Révisions')
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
  await scrollToBottom()

  try {
    await savePrompt(currentChatId, promptText)
    const context = await queryVectorStore(promptText)
    const conversationForMistral = [...messages.value]

    if (context) {
      const augmentedContent = `Tu es un assistant pédagogique. Voici des extraits pertinents issus des cours de l'étudiant pour t'aider à répondre.

PRIORITÉ : Utilise ces informations en priorité si elles sont pertinentes.
FLEXIBILITÉ : Si les extraits ne suffisent pas ou si la question demande une explication générale (ex: un calcul de maths), utilise tes connaissances générales pour compléter la réponse et aider l'étudiant au mieux.

DOCUMENTS DE RÉFÉRENCE :
${context}

QUESTION DE L'ÉTUDIANT :
${promptText}`

      conversationForMistral[conversationForMistral.length - 1] = {
        role: 'user',
        content: augmentedContent,
      }
    }

    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: '',
    }
    messages.value.push(assistantMessage)

    let fullResponse = ''
    const stream = chatWithMistralStream(conversationForMistral)
    const messageIndex = messages.value.length - 1

    for await (const chunk of stream) {
      fullResponse += chunk
      messages.value[messageIndex] = {
        role: 'assistant',
        content: fullResponse,
      }
      await scrollToBottom()
    }

    await savePrompt(currentChatId, fullResponse, 'assistant')
  } catch (error) {
    console.error('Failed to process message:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="flex-1 flex flex-col h-full bg-slate-50 text-slate-900">
    <div ref="chatContainer" class="flex-1 overflow-y-auto p-8 space-y-6">
      <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center">
        <div class="w-16 h-16 bg-blue-600/15 rounded-full flex items-center justify-center mb-4">
          <span class="text-2xl">🤖</span>
        </div>
        <h2 class="text-2xl font-semibold">Prêt à réviser ?</h2>
        <p class="text-slate-600 mt-2">Pose une question sur tes documents indexés.</p>
      </div>

      <div
        v-for="(message, index) in messages"
        :key="index"
        class="flex gap-4"
        :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          v-if="message.role === 'assistant'"
          class="flex-shrink-0 w-8 h-8 bg-blue-600/15 rounded-full flex items-center justify-center"
        >
          <span class="text-sm">🤖</span>
        </div>
        
        <div
          class="max-w-xs lg:max-w-md xl:max-w-2xl px-4 py-3 rounded-lg prose prose-slate"
          :class="
            message.role === 'user'
              ? 'bg-blue-600 text-white rounded-br-none prose-invert'
              : 'bg-slate-200 text-slate-900 rounded-bl-none shadow-sm'
          "
        >
          <div class="markdown-content" v-html="renderMarkdown(message.content)"></div>
        </div>

        <div
          v-if="message.role === 'user'"
          class="flex-shrink-0 w-8 h-8 bg-slate-300 rounded-full flex items-center justify-center"
        >
          <span class="text-sm">👤</span>
        </div>
      </div>

      <div v-if="isLoading" class="flex gap-4">
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

<style>
.markdown-content p {
  margin-bottom: 0.5rem;
}
.markdown-content p:last-child {
  margin-bottom: 0;
}
.markdown-content ul, .markdown-content ol {
  padding-left: 1.5rem;
  margin-bottom: 0.5rem;
}
.markdown-content ul {
  list-style-type: disc;
}
.markdown-content strong {
  font-weight: 700;
}
.prose-invert strong {
  color: white;
}
</style>