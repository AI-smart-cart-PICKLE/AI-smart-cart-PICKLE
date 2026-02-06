import { defineStore } from 'pinia'
import api from '@/api/axios'   // ✅ 이걸로 교체

export const useRecommendationStore = defineStore('recommendation', {
  state: () => ({
    recipes: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchByCart(cartSessionId) {
      if (!cartSessionId) return
      
      this.loading = true
      this.error = null

      try {
        // 기존 by-product 대신 새로 만든 by-cart API 호출
        const res = await api.get(`recommendations/by-cart/${cartSessionId}`)
        this.recipes = res.data
      } catch (e) {
        this.error = '장바구니 기반 추천을 불러오지 못했습니다.'
        console.error(e)
      } finally {
        this.loading = false
      }
    },

    async fetchByProduct(productId, cartSessionId) {

    async selectRecipe(recipeId, sessionId) {
      if (!sessionId) return
      try {
        await api.post(`carts/${sessionId}/select-recipe`, null, {
          params: { recipe_id: recipeId }
        })
        return true
      } catch (e) {
        console.error('레시피 선택 실패:', e)
        return false
      }
    },

    clear() {
      this.recipes = []
    }
  }
})
