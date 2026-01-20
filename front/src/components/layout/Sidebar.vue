<template>
  <div class="w-64 h-full bg-white border-r border-slate-200 p-6 flex flex-col">
    <h2 class="text-xl font-semibold text-slate-900 mb-8">Project-web-ai</h2>
    <div class="space-y-4 flex-1">
      <div class="text-slate-600 text-xs uppercase font-semibold tracking-widest">Documents</div>
      <div class="py-2 px-3 bg-blue-50 rounded-lg text-blue-600 text-sm font-medium">📚 Cours de Maths</div>
      <div class="py-2 px-3 hover:bg-slate-100 rounded-lg text-slate-700 text-sm cursor-pointer transition-colors">🧬 Biologie</div>
    </div>

    <!-- Section d'upload en bas -->
    <div class="mt-auto pt-6 border-t border-slate-200">
      <input 
        type="file" 
        ref="fileInput" 
        accept=".pdf"
        multiple
        class="hidden" 
        @change="handleFileUpload"
      />
      <button 
        @click="triggerFileInput"
        class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m6.75 12-3-3m0 0-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
        </svg>
        <span>Ajouter des PDF</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const fileInput = ref<HTMLInputElement | null>(null)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  
  if (files && files.length > 0) {
    console.log('Fichiers sélectionnés:', Array.from(files).map(f => f.name))
    // TODO: Implémenter l'upload vers le backend
  }
}
</script>