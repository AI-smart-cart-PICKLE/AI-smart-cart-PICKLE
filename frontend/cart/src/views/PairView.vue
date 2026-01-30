<script setup>
import api from '@/api/axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const pairCart = async () => {
  // 1️⃣ 임시 세션 생성
  const res = await api.post('/api/carts/')
  const cartSessionId = res.data.cart_session_id

  // 2️⃣ 세션 저장
  localStorage.setItem('cart_session_id', cartSessionId)

  // 3️⃣ 대시보드 이동
  router.push('/')
}
</script>

<template>
  <div class="flex flex-col items-center justify-center h-full">
    <h1 class="text-2xl font-bold mb-4">카트를 시작하려면 로그인하세요</h1>

    <!-- 나중에 QR로 대체 -->
    <button
      class="bg-green-600 text-white px-6 py-3 rounded"
      @click="pairCart"
    >
      임시 로그인 (개발용)
    </button>
  </div>
</template>
