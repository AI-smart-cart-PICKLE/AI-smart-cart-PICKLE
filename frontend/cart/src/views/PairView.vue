<script setup>
import { ref } from 'vue'
import LoginModal from '@/components/modals/LoginModal.vue'

const showLoginModal = ref(false)

const handleLoginClose = () => {
  showLoginModal.value = false
  // LoginModal 내부에서 이미 router.push('/')를 수행하므로 여기서는 추가 동작 불필요
}
</script>

<template>
  <div class="flex flex-col items-center justify-center h-full bg-slate-50">
    <div class="text-center mb-10">
      <h1 class="text-3xl font-black text-slate-800 mb-2">Pickle Smart Cart</h1>
      <p class="text-slate-400 font-medium">쇼핑을 시작하려면 로그인하세요</p>
    </div>

    <!-- QR 코드 스캔 대신 버튼으로 대체 -->
    <button
      class="px-8 py-4 bg-primary text-white rounded-[20px] font-bold text-lg shadow-xl shadow-primary/30 hover:scale-105 transition-transform"
      @click="showLoginModal = true"
    >
      시작하기 (로그인)
    </button>
    
    <p class="mt-6 text-sm text-slate-400">
      QR 코드를 스캔하여 <br/>카트와 연동할 수 있습니다.
    </p>

    <!-- 로그인 모달 -->
    <LoginModal v-if="showLoginModal" @close="handleLoginClose" />
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
