<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import CheckoutModal from '@/components/modals/CheckoutModal.vue'
import PaymentQRModal from '@/components/modals/PaymentQRModal.vue'

const cartStore = useCartStore()
const showCheckoutModal = ref(false)
const showQRModal = ref(false)
const currentPaymentData = ref(null)

const openCheckoutModal = () => {
  showCheckoutModal.value = true
}

const handleCheckoutSuccess = (paymentData) => {
  currentPaymentData.value = paymentData
  showQRModal.value = true
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
    <!-- ... 기존 코드 ... -->
    <div class="flex items-center gap-6">
      <!-- ... -->
    </div>

    <!-- RIGHT : 결제 버튼 -->
    <button
      @click="openCheckoutModal"
      class="
        px-8 py-2.5
        bg-violet-500 text-white
        rounded-xl
        font-bold text-base
        hover:bg-violet-600
        active:scale-95
        transition-all
        shadow-md
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
      :paymentData="currentPaymentData"
      @close="showQRModal = false"
    />
  </div>
</template>
