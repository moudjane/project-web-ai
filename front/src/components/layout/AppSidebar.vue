<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '@/firebaseConfig'
import { signOut } from 'firebase/auth'

const router = useRouter()
const fileInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => {
      const result = reader.result as string
      if (result) {
        const base64String = result.split(',')[1]
        if (base64String) {
          resolve(base64String)
        } else {
          reject(new Error("Impossible de convertir le fichier en base64"))
        }
      } else {
        reject(new Error("Le fichier est vide"))
      }
    }
    reader.onerror = (error) => reject(error)
  })
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  
  if (files && files.length > 0) {
    const file = files[0]
    
    if (!file) return
    if (file.type !== 'application/pdf') {
      alert("Veuillez sélectionner un fichier PDF.")
      return
    }

    const user = auth.currentUser
    if (!user) {
      alert("Vous devez être connecté pour ajouter des documents.")
      router.push('/login')
      return
    }

    try {
      isUploading.value = true
      
      const base64Data = await fileToBase64(file)

      const response = await fetch('http://localhost:8000/upload-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pdf_base64: base64Data,
          user_id: user.uid,
          filename: file.name
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Erreur lors de l'indexation")
      }

      const result = await response.json()
      console.log('Réponse du serveur:', result)
      alert(`Succès ! PDF indexé (${result.pages_processed} pages).`)

    } catch (error: any) {
      console.error('Erreur upload:', error)
      alert(`Erreur : ${error.message}`)
    } finally {
      isUploading.value = false
      if (fileInput.value) fileInput.value.value = ''
    }
  }
}
const handleLogout = async () => {
  try {
    await signOut(auth)
    router.push('/login')
  } catch (error) {
    console.error('Erreur lors de la déconnexion:', error)
  }
}
</script>

<template>
  <div class="w-64 h-full bg-white border-r border-slate-200 p-6 flex flex-col">
    <div class="flex items-center justify-between mb-8">
      <h2 class="text-xl font-bold text-slate-900 tracking-tight">CogniStack</h2>
      <button 
        class="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow-sm"
        title="Nouvelle discussion"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5 text-white">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
      </button>
    </div>
    
    <div class="space-y-4 flex-1 overflow-y-auto">
      <div class="text-slate-400 text-[10px] uppercase font-bold tracking-[0.2em] px-1">Tes Documents</div>
      <div class="py-2.5 px-3 bg-blue-50 rounded-xl text-blue-600 text-sm font-semibold flex items-center gap-2 border border-blue-100">
        <span>📚</span> Cours de Maths
      </div>
      <div class="py-2.5 px-3 hover:bg-slate-50 rounded-xl text-slate-600 text-sm font-medium cursor-pointer transition-colors flex items-center gap-2 border border-transparent">
        <span>🧬</span> Biologie
      </div>
    </div>

    <div class="mt-auto pt-6 border-t border-slate-100 space-y-3">
      <input 
        type="file" 
        ref="fileInput" 
        accept=".pdf"
        class="hidden" 
        @change="handleFileUpload"
      />
      
      <button 
        @click="triggerFileInput"
        :disabled="isUploading"
        class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold transition-all shadow-md shadow-blue-100 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="isUploading" class="animate-spin text-lg">⏳</span>
        <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m6.75 12-3-3m0 0-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
        </svg>
        <span>{{ isUploading ? 'Analyse...' : 'Ajouter un PDF' }}</span>
      </button>

      <button 
        @click="handleLogout"
        class="w-full py-3 px-4 bg-slate-50 hover:bg-red-50 hover:text-red-600 text-slate-500 rounded-xl font-semibold transition-colors flex items-center justify-center gap-2 border border-slate-100"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9" />
        </svg>
        <span>Se déconnecter</span>
      </button>
    </div>
  </div>
</template>