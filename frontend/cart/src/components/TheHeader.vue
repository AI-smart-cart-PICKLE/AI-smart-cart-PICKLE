<script setup>
import { ref, computed } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'

const cartStore = useCartStore()
const authStore = useAuthStore()
const uiStore = useUIStore()

// 🔽 드롭다운 상태
const showUserMenu = ref(false)

// 🛒 카트 디바이스 코드
const cartDeviceCode = computed(() =>
  cartStore.cartSession?.device_code ?? '-'
)

// 👤 유저 닉네임
const userNickname = computed(() =>
  authStore.user?.nickname ?? 'Guest'
)

// 🔐 로그아웃 (❗ URL 이동 없음)
const logout = async () => {
  showUserMenu.value = false

  // 1️⃣ 인증 정보 제거
  await authStore.logout()

  // 2️⃣ 로그인 모달 오픈
  uiStore.openLoginModal()
}
</script>

<template>
  <header
    class="h-16 px-8 flex items-center justify-between
           bg-white border-b border-slate-100
           sticky top-0 z-10"
  >
    <!-- Left -->
    <div class="flex items-center gap-3">
      <div class="bg-violet-500 p-2 rounded-xl">
        <span class="material-icons-round text-white">
          shopping_basket
        </span>
      </div>
      <h1 class="text-xl font-extrabold text-violet-500 tracking-tight">
        Pickle Dashboard
      </h1>
    </div>

    <!-- Right -->
    <div class="flex items-center gap-8">
      <!-- Cart ID -->
      <div class="flex flex-col items-end">
        <span
          class="text-[10px] font-bold text-slate-400
                 uppercase tracking-widest leading-none"
        >
          Cart ID
        </span>
        <span class="text-sm font-bold text-slate-700">
          {{ cartDeviceCode }}
        </span>
      </div>

      <div class="h-8 w-px bg-slate-100"></div>

      <!-- User -->
      <div class="relative flex items-center gap-3">
        <div class="text-right">
          <p class="text-xs font-bold text-slate-900 leading-none">
            {{ userNickname }}
          </p>
        </div>

        <!-- 프로필 버튼 -->
        <button @click="showUserMenu = !showUserMenu">
          <img
            alt="User Profile"
            class="w-10 h-10 rounded-full border-2 border-primary/20"
            src="@/assets/pickle-logo.png"
          />
        </button>

        <!-- 드롭다운 메뉴 -->
        <div
          v-if="showUserMenu"
          class="absolute right-0 top-12 w-32
                 rounded-xl bg-white shadow-lg border
                 text-sm z-50"
        >
          <button
            class="w-full px-4 py-2 text-left hover:bg-slate-100"
            @click="logout"
          >
            로그아웃
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
