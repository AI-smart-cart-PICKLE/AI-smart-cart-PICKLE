<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRecommendationStore } from '@/stores/recommendation'
import { useCartStore } from '@/stores/cart'
import RecipeCard from '@/components/RecipeCard.vue'
import RecipeDetailModal from '@/components/modals/RecipeDetailModal.vue'


const recStore = useRecommendationStore()
const cartStore = useCartStore()

/* 기준 상품: 가장 최근 담긴 상품 */
const baseProductId = computed(() => {
  if (!cartStore.cartItems.length) return null
  return cartStore.cartItems[cartStore.cartItems.length - 1].product_id
})

watch(
  () => baseProductId.value,
  (productId) => {
    if (!productId) {
      recStore.clear()
      return
    }

    recStore.fetchByProduct(
      productId,
      cartStore.cartSession?.cart_session_id
    )
  },
  { immediate: true }
)

const selectedRecipe = ref(null)
const openRecipe = (recipe) => {
  selectedRecipe.value = recipe
}
const closeRecipe = () => {
  selectedRecipe.value = null
}
</script>

<template>
  <section
    class="bg-white rounded-3xl border p-6
          flex flex-col
          max-h-[300px]"
  >

    <h2 class="text-xl font-bold mb-4">🍽 추천 레시피</h2>

    <!-- 로딩 -->
    <div v-if="recStore.loading" class="text-slate-400 text-sm">
      AI가 레시피를 분석 중입니다...
    </div>

    <!-- 없음 -->
    <div v-else-if="recStore.recipes.length === 0" class="text-slate-400 text-sm">
      추천 가능한 레시피가 없습니다.
    </div>

    <!-- 레시피 리스트 -->
    <div
      v-else
      class="grid grid-cols-2 gap-3
            max-h-[220px] overflow-y-auto"
    >
      <RecipeCard
        v-for="recipe in recStore.recipes"
        :key="recipe.recipe_id"
        :recipe="recipe"
        @click="openRecipe(recipe)"
      />
      <RecipeDetailModal
        v-if="selectedRecipe"
        :recipe="selectedRecipe"
        @close="closeRecipe"
      />

    </div>


  </section>
</template>
