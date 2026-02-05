import { defineStore } from 'pinia'
import api from '@/api/axios'   // ✅ 이걸로 교체

export const useRecommendationStore = defineStore('recommendation', {
  state: () => ({
    recipes: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchByProduct(productId, cartSessionId) {
      this.loading = true
      this.error = null

      try {
        const res = await api.get(
          `recommendations/by-product/${productId}`,
          {
            params: cartSessionId
              ? { cart_session_id: cartSessionId }
              : {}
          }
        )
        this.recipes = res.data
      } catch (e) {
        this.error = '추천 레시피를 불러오지 못했습니다.'
        console.error(e)
      } finally {
        this.loading = false
      }
    },

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
