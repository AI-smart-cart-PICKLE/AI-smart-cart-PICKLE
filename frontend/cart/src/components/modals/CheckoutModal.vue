<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'

const emit = defineEmits(['close', 'success'])
const cartStore = useCartStore()

const loading = ref(false)
const errorMsg = ref('')

const confirmCheckout = async () => {
  loading.value = true
  errorMsg.value = ''

  try {
    // 실제 결제 요청 (무게 검증 없이 바로 요청)
    await cartStore.checkout()
    
    // 성공 시 부모에게 알림 (이후 페이지 이동 등 처리)
    emit('success')
    // 모달 닫기
    emit('close')

  } catch (e) {
    console.error(e)
    errorMsg.value = e.response?.data?.detail || '결제 요청 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center
           bg-slate-900/60 backdrop-blur-sm"
  >
    <div
      class="w-[480px] bg-white rounded-[32px] p-8 shadow-2xl
             flex flex-col items-center text-center animate-in fade-in zoom-in duration-200"
    >
      <!-- 아이콘 -->
      <div class="mb-6 w-20 h-20 rounded-full bg-violet-100 flex items-center justify-center">
        <span class="material-icons-round text-4xl text-violet-500">
          payments
        </span>
      </div>

      <!-- 타이틀 -->
      <h2 class="text-2xl font-black text-slate-800 mb-2">
        결제를 진행할까요?
      </h2>
      
      <!-- 설명 -->
      <p class="text-slate-500 font-medium mb-8 leading-relaxed">
        현재 장바구니에 담긴 상품으로 <br/>
        결제(PG) 요청을 보냅니다.
      </p>

      <!-- 에러 메시지 -->
      <p v-if="errorMsg" class="text-red-500 font-bold text-sm mb-4">
        {{ errorMsg }}
      </p>

      <!-- 버튼 영역 -->
      <div class="flex gap-4 w-full">
        <button
          @click="$emit('close')"
          :disabled="loading"
          class="flex-1 py-4 rounded-2xl bg-slate-100 text-slate-600 font-bold text-lg
                 hover:bg-slate-200 transition-colors disabled:opacity-50"
        >
          취소
        </button>

        <button
          @click="confirmCheckout"
          :disabled="loading"
          class="flex-1 py-4 rounded-2xl bg-violet-500 text-white font-bold text-lg
                 hover:bg-violet-400 transition-colors shadow-lg shadow-violet-500/30
                 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          <span v-if="loading" class="material-icons-round animate-spin">sync</span>
          <span>{{ loading ? '요청 중...' : '결제하기' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>
