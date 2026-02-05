<script setup>
import { onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  url: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close'])

// ESC 키로 닫기
const handleEsc = (e) => {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => window.addEventListener('keydown', handleEsc))
onBeforeUnmount(() => window.removeEventListener('keydown', handleEsc))
</script>

<template>
  <div class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col relative">
      
      <!-- 헤더 -->
      <div class="px-6 py-4 border-b flex items-center justify-between bg-yellow-400">
        <div class="flex items-center gap-2">
          <img src="https://developers.kakao.com/assets/img/about/logos/kakaopay/payment/icon_pay_72x72.png" alt="kakaopay" class="w-8 h-8" />
          <h2 class="text-lg font-bold text-slate-900">카카오페이 결제</h2>
        </div>
        <button @click="emit('close')" class="p-2 hover:bg-black/10 rounded-full transition-colors">
          <span class="material-icons-round text-slate-900">close</span>
        </button>
      </div>

      <!-- 본문 (Iframe) -->
      <div class="flex-1 bg-white p-4 flex flex-col items-center">
        <p class="text-sm text-slate-500 mb-4 text-center">
          아래 화면의 QR 코드를 휴대폰으로 스캔하여 결제를 완료해주세요.
        </p>
        
        <div class="w-full h-[500px] border rounded-xl overflow-hidden shadow-inner relative">
          <iframe 
            :src="url" 
            class="w-full h-full border-none"
            allow="payment"
          ></iframe>
        </div>
      </div>

      <!-- 하단 안내 -->
      <div class="px-6 py-4 bg-slate-50 border-t">
        <p class="text-[11px] text-slate-400 text-center leading-relaxed">
          결제가 완료되면 모바일 앱에서 확인 버튼을 눌러주세요.<br/>
          창을 닫으려면 우측 상단의 X 버튼이나 ESC 키를 눌러주세요.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Round');
</style>