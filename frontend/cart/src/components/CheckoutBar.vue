<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import CheckoutModal from '@/components/modals/CheckoutModal.vue'

const cartStore = useCartStore()
const showCheckoutModal = ref(false)

const openCheckoutModal = () => {
  showCheckoutModal.value = true
}

const handleCheckoutSuccess = () => {
  // TODO: 이후 실제 결제 완료 페이지로 이동하거나,
  // 결제 대기 상태 화면(QR 등)을 띄워야 함.
  // 우선은 간단히 알림만.
  alert('결제 요청이 정상적으로 처리되었습니다.')
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
    <!-- LEFT : 금액 / 수량 -->
    <div class="flex items-center gap-6">
      <div>
        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
          Total Amount
        </p>
        <p class="text-2xl font-black text-green-400">
          {{ cartStore.estimatedTotal.toLocaleString() }}원
        </p>
      </div>

      <div class="h-8 w-px bg-slate-700"></div>

      <div>
        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
          Items
        </p>
        <p class="text-xl font-bold text-white">
          {{ cartStore.totalQuantity }}개
        </p>
      </div>
    </div>

    <!-- RIGHT : 결제 버튼 -->
    <button
      @click="openCheckoutModal"
      class="
        px-8 py-2.5
        bg-green-400 text-slate-900
        rounded-xl
        font-bold text-base
        hover:bg-green-300
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
  </div>
</template>
