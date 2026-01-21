import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '@/firebaseConfig'
import { onAuthStateChanged } from 'firebase/auth'
import ChatView from '../views/ChatView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'chat',
      component: ChatView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guestOnly: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { guestOnly: true }
    }
  ]
})

const getCurrentUser = () => {
  return new Promise((resolve, reject) => {
    const removeListener = onAuthStateChanged(
      auth,
      (user) => {
        removeListener()
        resolve(user)
      },
      reject
    )
  })
}

// Navigation Guard
router.beforeEach(async (to, from, next) => {
  const user = await getCurrentUser()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const guestOnly = to.matched.some(record => record.meta.guestOnly)

  if (requiresAuth && !user) {
    next('/login')
  } else if (guestOnly && user) {
    next('/')
  } else {
    next()
  }
})

export default router