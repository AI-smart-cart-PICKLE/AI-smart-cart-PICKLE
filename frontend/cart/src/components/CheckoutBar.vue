<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import CheckoutModal from '@/components/modals/CheckoutModal.vue'
import PaymentQRModal from '@/components/modals/PaymentQRModal.vue'

const cartStore = useCartStore()
const showCheckoutModal = ref(false)
const showQRModal = ref(false)
const qrUrl = ref('')

const openCheckoutModal = () => {
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
  <!-- ✅ 결제 바 -->
  <div
    class="
      w-full
      max-w-[900px]
      mx-auto
      bg-slate-900
      px-6 py-4
      rounded-2xl
      shadow-lg
      flex items-center justify-between
    "
  >
    <!-- LEFT : 총 금액 정보 -->
    <div class="flex items-center gap-6">
      <div class="flex flex-col">
        <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">Estimated Total</span>
        <div class="flex items-baseline gap-1">
          <span class="text-2xl font-black text-white">
            {{ cartStore.estimatedTotal.toLocaleString() }}
          </span>
          <span class="text-sm font-bold text-slate-400">원</span>
        </div>
      </div>

      <div class="h-10 w-px bg-slate-700"></div>

      <div class="flex flex-col">
        <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">Items</span>
        <span class="text-lg font-bold text-slate-300">
          {{ cartStore.totalQuantity }} 개
        </span>
      </div>
    </div>

    <!-- RIGHT : 결제 버튼 -->
    <button
      @click="openCheckoutModal"
      class="
        px-8 py-3
        bg-violet-500 text-white
        rounded-xl
        font-bold text-lg
        hover:bg-violet-600
        active:scale-95
        transition-all
        shadow-lg shadow-violet-500/30
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