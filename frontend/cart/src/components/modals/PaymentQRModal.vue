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
    @click.self="emit('close')"
  >
    <!-- ✅ 모달 (헤더/푸터 없이 iframe만 존재) -->
    <div
      class="bg-white rounded-[32px] shadow-2xl
             w-full max-w-[430px] h-[520px] overflow-hidden relative"
    >
      <!-- 닫기 버튼 (플로팅) -->
      <button
        @click="emit('close')"
        class="absolute top-4 right-4 z-10 p-2 rounded-full 
               bg-black/5 hover:bg-black/10 transition-colors"
      >
        <span class="material-icons-round text-slate-400 text-xl">
          close
        </span>
      </button>

      <!-- iframe 컨테이너 -->
      <div class="w-full h-full flex items-center justify-center bg-white">
        <iframe
          :src="url"
          class="w-full h-full border-none"
          allow="payment"
        ></iframe>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Round');

/* iframe 내부의 여백이나 스크롤바를 숨기기 위한 스타일 */
iframe {
  overflow: hidden;
}
</style>