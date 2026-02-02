<script setup>
import { ref } from 'vue'
import FindProductModal from '@/components/modals/FindProductModal.vue'
import ManualAddModal from '@/components/modals/ManualAddModal.vue'

const showFindProduct = ref(false)
const showManualAdd = ref(false)

</script>

<template>
  <div class="bg-white rounded-3xl border p-4 flex gap-3">
    
    <!-- 📍 위치 찾기 -->
    <button
      class="flex-1 py-3 rounded-xl bg-slate-100 font-bold text-sm"
      @click="showFindProduct = true"
    >
      📍 위치 찾기
    </button>

    <!-- ➕ 상품 추가 -->
    <button
      class="flex-1 py-3 rounded-xl bg-green-400 font-bold text-sm"
      @click="showManualAdd = true"
    >
      ➕ 상품 추가
    </button>

    <!-- 🔍 맵 전용 모달 -->
    <FindProductModal
      v-if="showFindProduct"
      :highlightZone="highlightZone"
      @close="showFindProduct = false"
    />

    <!-- ➕ 수동 추가 -->
    <ManualAddModal
      v-if="showManualAdd"
      @close="showManualAdd = false"
    />
  </div>
</template>
