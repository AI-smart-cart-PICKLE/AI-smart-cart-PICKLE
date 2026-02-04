<script setup>
import { ref } from 'vue'
import LocationModal from './LocationModal.vue'

defineProps({
  recipe: Object
})

const emit = defineEmits(['close'])

const showLocationModal = ref(false)
const selectedIngredient = ref(null)

const openLocationModal = (ingredient) => {
  selectedIngredient.value = ingredient
  showLocationModal.value = true
}
</script>

<template>
  <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
    <div class="bg-white w-[900px] h-[520px] rounded-3xl p-6 overflow-hidden">

      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold">{{ recipe.title }}</h2>
        <button @click="emit('close')">✕</button>
      </div>

      <!-- 재료 리스트 -->
      <div class="grid grid-cols-4 gap-3 overflow-y-auto h-full">
        <div
          v-for="ing in recipe.ingredients"
          :key="ing.product_id"
          class="border rounded-xl p-2 flex flex-col items-center justify-between h-[160px]"
          :class="ing.is_owned ? 'bg-green-50' : 'bg-white'"
        >
          <!-- 상태 아이콘 -->
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center
                   text-white text-sm font-bold"
            :class="ing.is_owned ? 'bg-green-400' : 'bg-slate-300'"
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
            :class="ing.is_owned ? 'text-green-600' : 'text-red-400'"
          >
            {{ ing.is_owned ? '담김' : '미보유' }}
          </span>

          <!-- 📍 위치 찾기 버튼 -->
          <button
            class="w-full py-1 mt-1 text-[11px] font-bold
                   rounded-lg bg-slate-100 hover:bg-slate-200"
            @click="openLocationModal(ing)"
          >
            📍 위치 찾기
          </button>
        </div>
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
