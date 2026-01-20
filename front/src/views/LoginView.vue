<template>
  <div class="min-h-dvh bg-white flex items-center justify-center p-4 font-sans text-slate-900">
    
    <div class="bg-white border border-slate-200 rounded-2xl shadow-xl p-8 w-full max-w-md relative">
      
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-slate-900 tracking-tight">Login</h1>
        <p class="text-slate-500 mt-2 text-sm font-medium">Accède à ton assistant d'étude</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label for="email" class="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 px-1">
            Email
          </label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="etudiant@ecole.fr"
            required
            class="w-full px-4 py-3 bg-white border border-slate-200 text-slate-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 transition-all placeholder:text-slate-300"
          />
        </div>

        <div>
          <label for="password" class="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 px-1">
            Mot de passe
          </label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="••••••••"
            required
            class="w-full px-4 py-3 bg-white border border-slate-200 text-slate-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 transition-all placeholder:text-slate-300"
          />
        </div>

        <button
          type="submit"
          class="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-all shadow-md shadow-blue-200 active:scale-[0.98]"
        >
          Se connecter
        </button>
      </form>
      
      <p class="text-center text-slate-500 text-sm">
        Pas de compte ?
        <router-link to="/register" class="text-blue-600 hover:underline font-bold transition-colors">
          Créer un accès
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')
const rememberMe = ref(false)

const handleLogin = async () => {
  // Redirige vers la page principale
  router.push('/')
}
</script>