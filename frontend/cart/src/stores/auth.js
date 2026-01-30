import { defineStore } from 'pinia'
import api from '@/api/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null,
    user: null,
  }),
  actions: {
    async login(email, password) {
      const res = await api.post('/api/auth/login', { email, password })
      this.accessToken = res.data.access_token
    },
  },
})
