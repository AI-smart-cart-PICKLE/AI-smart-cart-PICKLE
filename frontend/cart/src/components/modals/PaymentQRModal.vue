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

onMounted(() => {
  window.addEventListener('keydown', handleEsc)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleEsc)
})
</script>

<template>
  <!-- ✅ 오버레이 -->
  <div
    class="fixed inset-0 z-[100] flex items-center justify-center
           bg-black/60 backdrop-blur-sm p-4"
  >
    <!-- ✅ 모달 -->
    <div
      class="bg-white rounded-3xl shadow-2xl
             w-full max-w-md overflow-hidden flex flex-col relative"
    >
      <!-- ================= Header ================= -->
      <div
        class="px-6 py-4 flex items-center justify-between
               bg-yellow-400 border-b"
      >
        <div class="flex items-center gap-2">
          <img
            src="https://developers.kakao.com/assets/img/about/logos/kakaopay/payment/icon_pay_72x72.png"
            alt="kakaopay"
            class="w-8 h-8"
          />
          <h2 class="text-lg font-bold text-slate-900">
            카카오페이 결제
          </h2>
        </div>

        <button
          @click="emit('close')"
          class="p-2 rounded-full hover:bg-black/10 transition"
        >
          <span class="material-icons-round text-slate-900">
            close
          </span>
        </button>
      </div>

      <!-- ================= Body ================= -->
      <div class="flex-1 px-6 py-5 flex flex-col items-center">
        <p class="text-sm text-slate-500 text-center mb-4">
          휴대폰으로 QR 코드를 스캔하여<br />
          결제를 완료해주세요.
        </p>

        <!-- ✅ QR 영역만 노출 -->
        <div
          class="w-full max-w-[360px] h-[420px]
                 rounded-2xl border overflow-hidden
                 shadow-inner bg-white
                 flex items-center justify-center"
        >
          <!-- iframe 크롭용 래퍼 -->
          <div class="iframe-crop">
            <iframe
              :src="url"
              class="iframe-inner"
              allow="payment"
            ></iframe>
          </div>
        </div>
      </div>

      <!-- ================= Footer ================= -->
      <div class="px-6 py-4 bg-slate-50 border-t">
        <p
          class="text-[11px] text-slate-400 text-center leading-relaxed"
        >
          결제가 완료되면 모바일 앱에서 확인 버튼을 눌러주세요.<br />
          창을 닫으려면 우측 상단 X 또는 ESC 키를 누르세요.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Round');

/* 실제 카카오페이 iframe 크기 */
.iframe-inner {
  width: 420px;
  height: 720px;
  border: none;
}

/* ✅ 여기서 QR 영역만 보이도록 크롭 */
.iframe-crop {
  transform: scale(1.15) translateY(-120px);
  transform-origin: top center;
}
</style>
