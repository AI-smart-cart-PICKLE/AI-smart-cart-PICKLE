<script setup>
import { useCartStore } from '@/stores/cart'
import CartItem from '@/components/CartItem.vue'

const cartStore = useCartStore()
</script>

<template>
  <section
    class="h-full min-h-0 bg-white rounded-3xl border
            p-3 flex flex-col overflow-hidden"
  >
    <!-- 헤더 -->
    <div class="flex justify-between items-center mb-4 shrink-0">
      <h2 class="text-xl font-bold flex items-center gap-2">
        🛒 내 장바구니
      </h2>
      <button
        @click="cartStore.cancelCart()"
        class="text-sm text-slate-400 hover:text-red-500 underline"
      >
        세션 종료
      </button>
    </div>

    <!-- ✅ 스크롤 영역 -->
    <div class="flex-1 min-h-0 overflow-y-auto space-y-4 pr-2">
      <CartItem
        v-for="item in cartStore.cartItems"
        :key="item.cart_item_id"
        :item="item"
      />
    </div>
  </section>
</template>
