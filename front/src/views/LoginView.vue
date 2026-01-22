<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '@/firebaseConfig'
import { signInWithEmailAndPassword } from 'firebase/auth'

const router = useRouter()
const email = ref('')
const password = ref('')
const errorMsg = ref('')

const handleLogin = async () => {
  try {
    errorMsg.value = ''
    await signInWithEmailAndPassword(auth, email.value, password.value)
    router.push('/')
  } catch (error) {
    console.error('Erreur connexion:', error)
    errorMsg.value = "Email ou mot de passe incorrect."
  }
}
</script>

<template>
  <div class="min-h-dvh bg-white flex items-center justify-center p-6 font-sans text-slate-900">
    <div class="bg-white border border-slate-200 rounded-3xl shadow-xl p-10 w-full max-w-lg">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-extrabold text-slate-900 tracking-tight">CogniStack</h1>
        <p class="text-slate-400 mt-3 font-medium text-lg">Heureux de vous revoir</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-8">
        <div class="space-y-3">
          <label class="text-xs font-bold text-slate-400 uppercase tracking-widest px-1">Email</label>
          <input v-model="email" type="email" required placeholder="nom@exemple.com"
            class="w-full px-5 py-4 bg-white border border-slate-200 rounded-2xl focus:border-blue-600 focus:ring-4 focus:ring-blue-50 outline-none transition-all placeholder:text-slate-300" />
        </div>

        <div class="space-y-3">
          <label class="text-xs font-bold text-slate-400 uppercase tracking-widest px-1">Mot de passe</label>
          <input v-model="password" type="password" required placeholder="••••••••"
            class="w-full px-5 py-4 bg-white border border-slate-200 rounded-2xl focus:border-blue-600 focus:ring-4 focus:ring-blue-50 outline-none transition-all placeholder:text-slate-300" />
        </div>

        <p v-if="errorMsg" class="text-red-500 text-sm font-medium px-1">{{ errorMsg }}</p>

        <button type="submit"
          class="w-full py-5 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-bold text-lg shadow-lg shadow-blue-200 transition-all active:scale-[0.98]">
          Se connecter
        </button>
      </form>

      <div class="mt-10 text-center">
        <p class="text-slate-500 font-medium">
          Pas encore de compte ? 
          <router-link to="/register" class="text-blue-600 hover:text-blue-700 font-bold ml-1 decoration-2 underline-offset-4 hover:underline">
            S'inscrire
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>