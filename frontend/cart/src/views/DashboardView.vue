<script setup>
import { ref, onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'

import CartPanel from '@/components/CartPanel.vue'
import RecommendationPanel from '@/components/RecommendationPanel.vue'
import CheckoutBar from '@/components/CheckoutBar.vue'
import LoginModal from '@/components/modals/LoginModal.vue'
import ActionButtons from '@/components/ActionButtons.vue'
import WelcomePanel from '@/components/WelcomePanel.vue'

const cartStore = useCartStore()
const showLoginModal = ref(false)

const init = async () => {
  const sessionId = localStorage.getItem('cart_session_id')
  if (!sessionId) return

  try {
    await cartStore.fetchCartSession(sessionId)
  } catch (e) {
    localStorage.removeItem('cart_session_id')
    cartStore.cartSession = null
  }
}

onMounted(init)
</script>

<template>
  <!-- ✅ 헤더 제외 실제 대시보드 영역 -->
  <main
    class="w-[1280px] h-[536px]
           bg-slate-50 mx-auto overflow-hidden"
  >
    <!-- =========================
         본문 영역 (452px)
    ========================== -->
    <div
      class="h-[452px] px-6 pt-4
             grid grid-cols-12 gap-6 min-h-0"
    >
      <template v-if="cartStore.cartSession">
        <div class="col-span-7 h-full min-h-0">
          <CartPanel />
        </div>
        <div class="col-span-5 h-full min-h-0 flex flex-col gap-4">
          <!-- 추천 레시피 (위) -->
          <RecommendationPanel class="flex-none" />

          <!-- 액션 버튼 (아래) -->
          <ActionButtons />

          <!-- 결제 영역 -->
          <CheckoutBar
            v-if="cartStore.cartSession"
            class="flex-none"
          />
        </div>
      </template>
      <template v-else>
        <div class="col-span-12 h-full min-h-0">
          <WelcomePanel />
        </div>
      </template>
    </div>
  </main>
</template>


<style scoped>
.bg-primary { background-color: #4ade80; }
</style>
