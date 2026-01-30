<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'

const cartStore = useCartStore()

onMounted(() => {
  const sessionId = localStorage.getItem('cart_session_id')
  if (!sessionId) return

  cartStore.fetchCartSession(sessionId)
})
</script>

<template>
  <div v-if="cartStore.cartSession">
    <!-- 담은 상품 -->
    <CartItem
      v-for="item in cartStore.cartItems"
      :key="item.cart_item_id"
      :item="item"
    />

    <!-- 총액 -->
    <div>총액: {{ cartStore.estimatedTotal }}원</div>
  </div>
</template>
