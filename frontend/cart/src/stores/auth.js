import { defineStore } from 'pinia'
import api from '@/api/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
    user: null,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async login(email, password) {
      const res = await api.post('/api/auth/login', { email, password })
      
      const token = res.data.access_token
      this.accessToken = token
      localStorage.setItem('access_token', token)
      
      if (res.data.refresh_token) {
        localStorage.setItem('refresh_token', res.data.refresh_token)
      }

      await this.fetchMe()
    },

    logout() {
      this.accessToken = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('cart_session_id')
    },
    
    async fetchMe() {
      if (!this.accessToken) return
      try {
        const res = await api.get('/api/users/me')
        this.user = res.data
      } catch (e) {
        console.error("Failed to fetch user info:", e)
      }
    }
  },
})
