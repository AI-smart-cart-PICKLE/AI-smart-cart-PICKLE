<script setup>
import { computed } from 'vue'

const props = defineProps({
  paymentData: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

// 구글 차트 API를 사용한 QR 코드 URL 생성
const qrCodeUrl = computed(() => {
  const url = props.paymentData.next_redirect_mobile_url
  if (!url) return ''
  // 300x300 사이즈, URL 인코딩 적용
  return `https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl=${encodeURIComponent(url)}`
})

const close = () => {
  emit('close')
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center
           bg-slate-900/60 backdrop-blur-sm"
  >
    <div
      class="w-[520px] bg-white rounded-[40px] p-10 shadow-2xl
             flex flex-col items-center text-center animate-in fade-in zoom-in duration-300"
    >
      <!-- 상단 뱃지 -->
      <div class="mb-6 px-4 py-1.5 bg-amber-100 text-amber-700 rounded-full font-black text-xs uppercase tracking-widest">
        Payment Pending
      </div>

      <h2 class="text-3xl font-black text-slate-800 mb-2">
        QR 코드로 결제하기
      </h2>
      
      <p class="text-slate-500 font-medium mb-8 leading-relaxed">
        앱에서 QR 카메라를 켜고 아래 코드를 스캔하세요. <br/>
        카카오페이 결제 화면으로 이동합니다.
      </p>

      <!-- QR 코드 영역 -->
      <div class="mb-8 p-6 bg-slate-50 rounded-[32px] border-2 border-dashed border-slate-200">
        <div class="w-64 h-64 bg-white rounded-2xl flex items-center justify-center overflow-hidden shadow-inner">
          <img 
            v-if="qrCodeUrl" 
            :src="qrCodeUrl" 
            alt="Payment QR Code"
            class="w-full h-full object-contain"
          />
          <div v-else class="animate-pulse flex flex-col items-center text-slate-300">
            <span class="material-icons-round text-6xl">qr_code_2</span>
            <p class="text-xs font-bold mt-2">Generating QR...</p>
          </div>
        </div>
      </div>

      <!-- 안내 사항 -->
      <div class="flex items-start gap-3 text-left bg-blue-50 p-5 rounded-2xl mb-8 w-full">
        <span class="material-icons-round text-blue-500">info</span>
        <p class="text-blue-700 text-sm font-medium leading-snug">
          결제가 완료되면 앱에서 완료 메시지가 나타납니다. <br/>
          결제 중에는 이 창을 닫지 마세요.
        </p>
      </div>

      <!-- 닫기 버튼 -->
      <button
        @click="close"
        class="w-full py-4 rounded-2xl bg-slate-800 text-white font-bold text-lg
               hover:bg-slate-700 transition-colors shadow-lg"
      >
        창 닫기
      </button>
    </div>
  </div>
</template>
