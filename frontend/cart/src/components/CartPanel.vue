<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import CartItem from '@/components/CartItem.vue'

const cartStore = useCartStore()

// 세션 종료 모달 상태
const showCancelModal = ref(false)

// 세션 종료 확정
const confirmCancel = async () => {
  showCancelModal.value = false
  await cartStore.cancelCart()
}
</script>

<template>
  <!-- ⚠️ relative 필수 (모달 1280x600 내부 제한) -->
  <section
    class="relative h-full min-h-0 bg-white rounded-3xl border
           p-3 flex flex-col overflow-hidden"
  >
    <!-- ================= 헤더 ================= -->
    <div class="flex justify-between items-center mb-4 shrink-0">
      <h2 class="text-xl font-bold flex items-center gap-2">
        🛒 내 장바구니
      </h2>

      <button
        class="text-sm text-slate-400 hover:text-red-500 underline"
        @click="showCancelModal = true"
      >
        세션 종료
      </button>
    </div>

    <!-- ================= 장바구니 리스트 ================= -->
    <div class="flex-1 min-h-0 overflow-y-auto space-y-4 pr-2">
      <CartItem
        v-for="item in cartStore.cartItems"
        :key="item.cart_item_id"
        :item="item"
      />
    </div>

    <!-- ================= 세션 종료 확인 모달 ================= -->
    <div
      v-if="showCancelModal"
      class="absolute inset-0 z-50 flex items-center justify-center bg-black/40"
    >
      <div
        class="w-[420px] rounded-2xl bg-white p-6 shadow-xl text-center"
      >
        <h3 class="text-lg font-bold mb-3">
          장바구니 세션 종료
        </h3>

        <p class="text-sm text-slate-600 mb-6">
          장바구니 세션을 종료할까요?
        </p>

        <div class="flex justify-center gap-4">
          <button
            class="px-4 py-2 rounded-lg bg-slate-200 hover:bg-slate-300"
            @click="showCancelModal = false"
          >
            취소
          </button>

          <button
            class="px-4 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600"
            @click="confirmCancel"
          >
            확인
          </button>
        </div>
      </div>
    </div>
  </section>
</template>
