<!-- App.vue -->
<script setup>
import { RouterView, useRoute } from 'vue-router'
import { onMounted, watch } from 'vue'
import TheHeader from './components/TheHeader.vue'
import LoginModal from './components/modals/LoginModal.vue'

import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'

const authStore = useAuthStore()
const uiStore = useUIStore()
const route = useRoute()

const checkAuth = async () => {
  await authStore.fetchMe()

  if (!authStore.isAuthenticated && route.path !== '/pair') {
    uiStore.openLoginModal()
  }
}

onMounted(checkAuth)

// 경로가 바뀔 때마다 체크 (로그인 페이지가 아닌 곳으로 갈 때 로그인 유도)
watch(() => route.path, (newPath) => {
  if (!authStore.isAuthenticated && newPath !== '/pair') {
    uiStore.openLoginModal()
  } else if (newPath === '/pair') {
    uiStore.closeLoginModal()
  }
})
</script>

<template>
  <div
    class="bg-background-light text-slate-900 antialiased w-[1280px] h-[600px] relative border-x border-slate-100 mx-auto overflow-hidden font-display"
  >
    <TheHeader />
    <RouterView />

    <LoginModal
      v-if="uiStore.showLoginModal"
      @close="uiStore.closeLoginModal"
    />

  </div>
</template>

<style>
/* 폰트 이름 매핑 (Tailwind config가 없어도 작동하도록 CSS로 설정) */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.font-display {
  font-family: 'Plus Jakarta Sans', sans-serif;
}
</style>