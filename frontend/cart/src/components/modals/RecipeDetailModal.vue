<script setup>
import { ref } from 'vue'
import LocationModal from './LocationModal.vue'

defineProps({
  recipe: Object
})

const emit = defineEmits(['close', 'select'])

const showLocationModal = ref(false)
const selectedIngredient = ref(null)

const openLocationModal = (ingredient) => {
  selectedIngredient.value = ingredient
  showLocationModal.value = true
}

const selectRecipe = () => {
  emit('select', props.recipe.recipe_id)
}
</script>

<template>
  <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
    <div class="bg-white w-[900px] h-[600px] rounded-3xl p-6 overflow-hidden flex flex-col">

      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold">{{ recipe.title }}</h2>
        <button @click="emit('close')" class="text-2xl text-slate-400 hover:text-slate-600">✕</button>
      </div>

      <!-- 재료 리스트 -->
      <div class="grid grid-cols-4 gap-3 overflow-y-auto flex-1 mb-4">
        <div
          v-for="ing in recipe.ingredients"
          :key="ing.product_id"
          class="border rounded-xl p-2 flex flex-col items-center justify-between h-[160px]"
          :class="ing.is_owned ? 'bg-violet-50 border-violet-200' : 'bg-white'"
        >
          <!-- 상태 아이콘 -->
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center
                   text-white text-sm font-bold"
            :class="ing.is_owned ? 'bg-violet-500' : 'bg-slate-300'"
          >
            ✓
          </div>

          <!-- 재료명 -->
          <p class="text-xs text-center font-bold leading-tight">
            {{ ing.name }}
          </p>

          <!-- 보유 상태 -->
          <span
            class="text-[10px]"
            :class="ing.is_owned ? 'text-violet-600 font-bold' : 'text-red-400'"
          >
            {{ ing.is_owned ? '담김' : '미보유' }}
          </span>

          <!-- 📍 위치 찾기 버튼 -->
          <button
            class="w-full py-1 mt-1 text-[11px] text-black
                  rounded-lg
                  bg-violet-400 hover:bg-violet-300
                  transition-colors"
            @click="openLocationModal(ing)"
          >
            📍 위치 찾기
          </button>
        </div>
      </div>

      <!-- 레시피 선택 버튼 -->
      <div class="flex justify-center pt-2">
        <button
          @click="selectRecipe"
          class="bg-violet-600 text-white font-bold py-3 px-12 rounded-2xl
                 hover:bg-violet-700 transition-colors shadow-lg"
        >
          이 레시피로 요리하기 (앱에 저장)
        </button>
      </div>

      <!-- ✅ 모달은 여기! (v-for 밖) -->
      <LocationModal
        v-if="showLocationModal && selectedIngredient"
        :productId="selectedIngredient.product_id"
        @close="showLocationModal = false"
      />
    </div>
  </div>
</template>
