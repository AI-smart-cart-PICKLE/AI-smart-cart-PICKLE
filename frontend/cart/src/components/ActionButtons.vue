<script setup>
import { ref } from 'vue'
import FindProductModal from '@/components/modals/FindProductModal.vue'
import ManualAddModal from '@/components/modals/ManualAddModal.vue'
import CameraModal from '@/components/modals/CameraModal.vue'
import { useCartStore } from '@/stores/cart'

const showFindProduct = ref(false)
const showCamera = ref(false)
const showManualAdd = ref(false)

const cartStore = useCartStore()

async function onBarcodeDetected(barcode) {
  showCamera.value = false
  await cartStore.addItemByBarcode(barcode)
}

async function openCamera() {
  await navigator.mediaDevices.getUserMedia({ video: true })
  showCamera.value = true
}

// 바코드 실패 시
function onScanFail() {
  showCamera.value = false
  showManualAdd.value = true
}
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

    <!-- ➕ 상품 추가 (카메라) -->
    <button
      class="flex-1 py-3 rounded-xl bg-green-400 font-bold text-sm"
      @click="showCamera = true"
    >
      ➕ 상품 추가
    </button>

    <!-- 🔍 위치 찾기 모달 -->
    <FindProductModal
      v-if="showFindProduct"
      :highlightZone="highlightZone"
      @close="showFindProduct = false"
    />

    <!-- 📷 바코드 카메라 -->
    <CameraModal
      v-if="showCamera"
      @detected="onBarcodeDetected"
      @fail="onScanFail"
      @close="showCamera = false"
    />

    <!-- ➕ 수동 추가 (fallback) -->
    <ManualAddModal
      v-if="showManualAdd"
      @close="showManualAdd = false"
    />
  </div>
</template>
