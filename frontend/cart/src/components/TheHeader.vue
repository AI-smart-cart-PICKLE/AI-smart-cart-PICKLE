<script setup>
import { computed } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'

const cartStore = useCartStore()
const authStore = useAuthStore()

const cartDeviceCode = computed(() =>
  cartStore.cartSession?.device_code ?? '-'
)

const userNickname = computed(() =>
  authStore.user?.nickname ?? 'Guest'
)
</script>


<template>
  <header
    class="h-16 px-8 flex items-center justify-between
           bg-white border-b border-slate-100
           sticky top-0 z-10"
  >
    <!-- Left -->
    <div class="flex items-center gap-3">
      <div class="bg-primary p-2 rounded-xl">
        <span class="material-icons-round text-white">
          shopping_basket
        </span>
      </div>
      <h1 class="text-xl font-extrabold tracking-tight">
        Pickle
        <span class="text-primary text-sm font-bold ml-1 uppercase">
          Smart Dashboard
        </span>
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
      <div class="flex items-center gap-3">
        <div class="text-right">
          <p class="text-xs font-bold text-slate-900 leading-none">
            {{ userNickname }}
          </p>
        </div>
        <img
          alt="User Profile"
          class="w-10 h-10 rounded-full border-2 border-primary/20"
          src="@/assets/pickle-logo.png"
        />
      </div>
    </div>
  </header>
</template>
