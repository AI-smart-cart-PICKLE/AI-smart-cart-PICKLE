<script setup>
import { ref, computed } from 'vue'
import { useCartStore } from '@/stores/cart'
import CheckoutModal from '@/components/modals/CheckoutModal.vue'
import PaymentQRModal from '@/components/modals/PaymentQRModal.vue'

/* =========================
 * Store
 * ========================= */
const cartStore = useCartStore()

/* =========================
 * State
 * ========================= */
const showCheckoutModal = ref(false)
const showQRModal = ref(false)
const qrUrl = ref('')

/* =========================
 * Computed
 * ========================= */
const totalQuantity = computed(() => cartStore.totalQuantity)
const estimatedTotal = computed(() => cartStore.estimatedTotal)

/* =========================
 * Methods
 * ========================= */
const openCheckoutModal = () => {
  if (totalQuantity.value === 0) {
    alert('장바구니에 담긴 상품이 없습니다.')
    return
  }
  showCheckoutModal.value = true
}

// 결제 준비 API 성공 시 실행
const handleCheckoutSuccess = (paymentData) => {
  // 카카오페이 PC 결제 페이지 URL 추출
  if (paymentData && paymentData.next_redirect_pc_url) {
    qrUrl.value = paymentData.next_redirect_pc_url
    showQRModal.value = true
  } else {
    alert('결제 정보를 불러오지 못했습니다.')
  }
}
</script>

<template>
  <!-- ✅ Checkout Bar -->
  <div
    class="
      w-full max-w-[900px] mx-auto
      bg-slate-900
      px-6 py-4
      rounded-2xl
      shadow-lg
      flex items-center justify-between
    "
  >
    <!-- LEFT : 담은 물건 / 합계 정보 -->
    <div class="flex items-center gap-6 text-white">
      <!-- 담은 물건 -->
      <div class="flex flex-col">
        <span class="text-xs text-slate-400">담은 물건</span>
        <span class="text-lg font-bold">
          {{ totalQuantity }} 개
        </span>
      </div>

      <!-- 구분선 -->
      <div class="w-px h-10 bg-slate-700" />

      <!-- 합계 금액 -->
      <div class="flex flex-col">
        <span class="text-xs text-slate-400">합계 금액</span>
        <span class="text-xl font-bold">
          {{ estimatedTotal.toLocaleString() }} 원
        </span>
      </div>
    </div>

    <!-- RIGHT : 결제 버튼 -->
    <button
      @click="openCheckoutModal"
      :disabled="totalQuantity === 0"
      class="
        px-8 py-3
        bg-violet-500 text-white
        rounded-xl
        font-bold text-lg
        hover:bg-violet-600
        active:scale-95
        transition-all
        shadow-lg shadow-violet-500/30
        disabled:opacity-40
      "
    >
      결제하기
    </button>

    <!-- 결제 확인 모달 -->
    <CheckoutModal
      v-if="showCheckoutModal"
      @close="showCheckoutModal = false"
      @success="handleCheckoutSuccess"
    />

    <!-- QR 결제 대기 모달 -->
    <PaymentQRModal
      v-if="showQRModal"
      :url="qrUrl"
      @close="showQRModal = false"
    />
  </div>
</template>
