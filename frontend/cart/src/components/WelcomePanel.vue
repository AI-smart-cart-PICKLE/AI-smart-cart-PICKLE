<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'

const cartStore = useCartStore()
const loading = ref(false)

const startShopping = async () => {
  loading.value = true
  try {
    const res = await cartStore.createCartSession()
    localStorage.setItem('cart_session_id', res.cart_session_id)
  } catch (e) {
    console.error('Failed to start shopping:', e)
    alert('쇼핑을 시작하는 중 오류가 발생했습니다.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex flex-col items-center justify-center h-full w-full bg-white rounded-3xl border border-dashed border-slate-300">
    <div class="text-center p-8">
      <div class="mb-6 inline-flex items-center justify-center w-20 h-20 bg-primary/10 rounded-full">
        <span class="material-icons-round text-primary text-4xl">shopping_cart</span>
      </div>
      
      <h2 class="text-2xl font-black text-slate-800 mb-3">
        쇼핑을 시작할 준비가 되셨나요?
      </h2>
      
      <p class="text-slate-500 font-medium mb-8 max-w-xs mx-auto">
        새로운 장바구니 세션을 만들어 <br/> 스마트한 쇼핑을 경험해보세요.
      </p>

      <button
        @click="startShopping"
        :disabled="loading"
        class="px-10 py-4 bg-primary text-white rounded-[20px] font-bold text-lg 
               shadow-xl shadow-primary/30 hover:scale-105 active:scale-95 
               transition-all disabled:opacity-50 flex items-center gap-2 mx-auto"
      >
        <span v-if="loading" class="animate-spin material-icons-round">sync</span>
        <span>{{ loading ? '세션 생성 중...' : '쇼핑 시작하기' }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.bg-primary {
  background-color: #4ade80;
}
.text-primary {
  color: #4ade80;
}
.shadow-primary\/30 {
  --tw-shadow-color: rgb(74 222 128 / 0.3);
  --tw-shadow: var(--tw-shadow-colored);
}
</style>
