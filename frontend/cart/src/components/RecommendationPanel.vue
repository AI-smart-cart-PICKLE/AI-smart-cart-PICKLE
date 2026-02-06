<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRecommendationStore } from '@/stores/recommendation'
import { useCartStore } from '@/stores/cart'
import RecipeCard from '@/components/RecipeCard.vue'
import RecipeDetailModal from '@/components/modals/RecipeDetailModal.vue'


const recStore = useRecommendationStore()
const cartStore = useCartStore()

/* 세션 ID와 아이템 개수를 함께 감시 */
watch(
  [() => cartStore.cartSession?.cart_session_id, () => cartStore.cartItems.length],
  ([sessionId, itemCount]) => {
    console.log(`🔍 [DEBUG] 추천 트리거 확인 - Session: ${sessionId}, Items: ${itemCount}`)
    
    if (!sessionId || itemCount === 0) {
      recStore.clear()
      return
    }

    // 조건 충족 시 추천 요청
    recStore.fetchByCart(sessionId)
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

const handleSelectRecipe = async (recipeId) => {
  const sessionId = cartStore.cartSession?.cart_session_id
  if (!sessionId) return

  const success = await recStore.selectRecipe(recipeId, sessionId)
  if (success) {
    alert('레시피가 선택되었습니다. 앱의 "나의 레시피"에서 확인하실 수 있습니다.')
    closeRecipe()
  } else {
    alert('레시피 선택에 실패했습니다.')
  }
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
        @select="handleSelectRecipe"
      />

    </div>


  </section>
</template>
