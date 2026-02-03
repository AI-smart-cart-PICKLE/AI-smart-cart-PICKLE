// axios.js 
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config

    if (
      error.response?.status === 401 &&
      error.response?.data?.detail === 'Token expired' &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true

      try {
        const res = await api.post(
          '/auth/refresh',
          {},
          { withCredentials: true }
        )

        const newAccessToken = res.data.access_token
        localStorage.setItem('access_token', newAccessToken)

        originalRequest.headers.Authorization =
          `Bearer ${newAccessToken}`

        return api(originalRequest)
      } catch {
        localStorage.removeItem('access_token')

        window.dispatchEvent(new Event('auth-expired'))

        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
)

export default api
