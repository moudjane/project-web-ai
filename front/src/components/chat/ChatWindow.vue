<template>
  <div class="flex-1 flex flex-col h-full bg-slate-50 text-slate-900">
    <div class="flex-1 p-8 text-center flex flex-col items-center justify-center">
      <div class="w-16 h-16 bg-blue-600/15 rounded-full flex items-center justify-center mb-4">
        <span class="text-2xl">🤖</span>
      </div>
      <h2 class="text-2xl font-semibold">Prêt à réviser ?</h2>
      <p class="text-slate-600 mt-2">Pose une question sur tes documents indexés.</p>
    </div>

    <div class="p-6 border-t border-slate-200 bg-white/90 backdrop-blur-sm">
      <div class="flex items-center gap-4 w-full">
        <button class="flex-shrink-0 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>Nouvelle catégorie</span>
        </button>
        <input 
          type="text"
          placeholder="Ecris ton message ici..."
          class="flex-1 bg-white border border-slate-200 text-slate-900 rounded-lg py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all placeholder:text-slate-500 shadow-sm"
        />
        <button class="flex-shrink-0 p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>