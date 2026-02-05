<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'

import CartPanel from '@/components/CartPanel.vue'
import RecommendationPanel from '@/components/RecommendationPanel.vue'
import CheckoutBar from '@/components/CheckoutBar.vue'
import ActionButtons from '@/components/ActionButtons.vue'
import WelcomePanel from '@/components/WelcomePanel.vue'

const router = useRouter()
const cartStore = useCartStore()
let pollingTimer = null
let isPolling = false  // 중복 요청 방지 플래그

const init = async () => {
  const sessionId = localStorage.getItem('cart_session_id')
  
  // 세션 ID가 없으면 즉시 QR 화면으로
  if (!sessionId) {
    router.replace('/pair')
    return
  }

  try {
    await cartStore.fetchCartSession(sessionId)
  } catch (e) {
    localStorage.removeItem('cart_session_id')
    cartStore.cartSession = null
  }
}

// 🔄 주기적으로 세션 상태 확인 (결제 완료/취소 감지용)
const startPolling = () => {
  pollingTimer = setInterval(async () => {
    // 이전 요청이 진행 중이면 스킵 (요청 큐잉 방지)
    if (isPolling) {
      console.log('⏭️ [POLL] 이전 요청 진행 중, 스킵')
      return
    }

    const sessionId = localStorage.getItem('cart_session_id')
    if (!sessionId) return

    isPolling = true
    try {
      await cartStore.fetchCartSession(sessionId)
    } catch (e) {
      console.error('❌ [POLL] 폴링 에러:', e)
    } finally {
      isPolling = false  // 완료/실패 관계없이 플래그 해제
    }
  }, 1000) // 1초마다 시도 (단, 이전 요청 완료 후에만 실행)
}

// 👀 세션 상태 감시 -> 세션이 끊기면(null) QR 화면으로 이동
watch(() => cartStore.cartSession, (newSession) => {
  if (!newSession) {
    router.replace('/pair')
  }
})

onMounted(async () => {
  await init()
  startPolling()
})

onBeforeUnmount(() => {
  if (pollingTimer) clearInterval(pollingTimer)
})
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
