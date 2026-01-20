import { createRouter, createWebHistory } from 'vue-router'
// On importe directement la vue principale
import ChatView from '@/views/ChatView.vue' 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'chat',
      component: ChatView, // Ta page par défaut sera le chat
    },
    // {
    //   path: '/documents',
    //   name: 'documents',
    //   // On utilise le lazy-loading pour la gestion des documents
    //   component: () => import('@/views/DocumentsView.vue'),
    // },
  ],
})

export default router