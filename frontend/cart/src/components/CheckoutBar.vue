<script setup>
import { ref, computed } from 'vue'
import { useCartStore } from '@/stores/cart'
import CheckoutModal from '@/components/modals/CheckoutModal.vue'

/* =========================
 * Store
 * ========================= */
const cartStore = useCartStore()

/* =========================
 * State
 * ========================= */
const showCheckoutModal = ref(false)

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

/**
 * 🚀 카카오페이 결제창 열기
 * 브라우저 보안 정책을 고려하여 옵션을 최소화합니다.
 */
const handleCheckoutSuccess = (paymentData) => {
  if (paymentData && paymentData.next_redirect_pc_url) {
    const url = paymentData.next_redirect_pc_url
    
    // 카카오페이 권장 사이즈
    const width = 450
    const height = 650
    
    // 화면 중앙 정렬
    const left = (window.screen.width / 2) - (width / 2)
    const top = (window.screen.height / 2) - (height / 2)
    
    /**
     * ✅ [중요] 옵션을 너무 많이 주면 보안 정책에 걸릴 수 있음
     * 최소한의 옵션만 사용하여 표준 팝업으로 띄움
     */
    const popup = window.open(
      url, 
      'kakaoPayPopup', 
      `width=${width},height=${height},top=${top},left=${left},scrollbars=yes`
    )

    if (!popup || popup.closed || typeof popup.closed === 'undefined') {
      alert('팝업 차단이 설정되어 있습니다. 브라우저 설정에서 팝업을 허용해주세요.')
    }
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
  </div>
</template>