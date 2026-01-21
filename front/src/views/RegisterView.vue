<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '@/firebaseConfig'
import { createUserWithEmailAndPassword, updateProfile } from 'firebase/auth'

const router = useRouter()
const name = ref('')
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const isLoading = ref(false)

const handleRegister = async () => {
  if (!name.value || !email.value || !password.value) {
    errorMsg.value = "Tous les champs sont obligatoires."
    return
  }

  try {
    isLoading.value = true
    errorMsg.value = ""
    
    // 1. Création de l'utilisateur dans Firebase Auth
    const userCredential = await createUserWithEmailAndPassword(auth, email.value, password.value)
    
    // 2. Ajout du pseudo (displayName) au profil
    await updateProfile(userCredential.user, { 
      displayName: name.value 
    })
    
    console.log("Compte créé avec succès:", userCredential.user.uid)
    
    // 3. Redirection vers le chat
    router.push('/')
    
  } catch (err: any) {
    console.error("Erreur Firebase:", err.code)
    // Gestion des erreurs spécifiques pour aider l'utilisateur
    if (err.code === 'auth/email-already-in-use') {
      errorMsg.value = "Cet email est déjà utilisé."
    } else if (err.code === 'auth/weak-password') {
      errorMsg.value = "Le mot de passe doit faire au moins 6 caractères."
    } else if (err.code === 'auth/invalid-email') {
      errorMsg.value = "Format d'email invalide."
    } else {
      errorMsg.value = "Une erreur est survenue lors de l'inscription."
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-dvh bg-slate-50 flex items-center justify-center p-6 font-sans text-slate-900">
    <div class="bg-white border border-slate-200 rounded-3xl shadow-xl p-10 w-full max-w-lg relative">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-extrabold text-slate-900 tracking-tight">Rejoindre CogniStack</h1>
        <p class="text-slate-500 mt-3">Créez votre compte pour commencer</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-6">
        <div class="space-y-2">
          <label class="text-xs font-bold text-slate-400 uppercase tracking-widest px-1">Pseudo</label>
          <input v-model="name" type="text" required placeholder="Ex: Mathis"
            class="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:border-blue-600 focus:bg-white outline-none transition-all" />
        </div>

        <div class="space-y-2">
          <label class="text-xs font-bold text-slate-400 uppercase tracking-widest px-1">Email</label>
          <input v-model="email" type="email" required placeholder="votre@email.com"
            class="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:border-blue-600 focus:bg-white outline-none transition-all" />
        </div>

        <div class="space-y-2">
          <label class="text-xs font-bold text-slate-400 uppercase tracking-widest px-1">Mot de passe</label>
          <input v-model="password" type="password" required placeholder="••••••••"
            class="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:border-blue-600 focus:bg-white outline-none transition-all" />
        </div>

        <div v-if="errorMsg" class="bg-red-50 text-red-600 p-4 rounded-xl text-sm font-medium border border-red-100">
          ⚠️ {{ errorMsg }}
        </div>

        <button type="submit" :disabled="isLoading"
          class="w-full py-5 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-bold text-lg shadow-lg shadow-blue-100 transition-all disabled:opacity-50 flex items-center justify-center">
          <span v-if="isLoading" class="animate-spin mr-2">⏳</span>
          {{ isLoading ? 'Création en cours...' : 'Créer mon compte' }}
        </button>
      </form>

      <div class="mt-8 text-center">
        <p class="text-slate-500 font-medium">
          Déjà un compte ? 
          <router-link to="/login" class="text-blue-600 hover:underline font-bold">Se connecter</router-link>
        </p>
      </div>
    </div>
  </div>
</template>