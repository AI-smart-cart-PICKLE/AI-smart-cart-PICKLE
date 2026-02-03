// index.js
import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'
import PairView from '@/views/PairView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: DashboardView,
      meta: { requiresPairing: true },
    },
    {
      path: '/pair',
      component: PairView,
    },
  ],
})

router.beforeEach((to) => {
  if (to.meta.requiresPairing) {
    const cartSessionId = localStorage.getItem('cart_session_id')
    if (!cartSessionId) {
      return '/pair'
    }
  }
})

export default router
