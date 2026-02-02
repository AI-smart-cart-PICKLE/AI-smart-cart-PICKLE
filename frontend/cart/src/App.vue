<script setup>
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'    
import TheHeader from './components/TheHeader.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  authStore.fetchMe()
})
</script>

<template>
  <div class="bg-background-light text-slate-900 antialiased w-[1280px] h-[600px] relative border-x border-slate-100 mx-auto overflow-hidden font-display">
    <TheHeader />
    <RouterView />
  </div>
</template>

<style>
/* 폰트 이름 매핑 (Tailwind config가 없어도 작동하도록 CSS로 설정) */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.font-display {
  font-family: 'Plus Jakarta Sans', sans-serif;
}
</style>