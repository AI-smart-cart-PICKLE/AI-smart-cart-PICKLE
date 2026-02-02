<script setup>
import { useCartStore } from '@/stores/cart'
const cartStore = useCartStore()
</script>

<template>
  <!-- ✅ 결제 바 -->
  <div
    class="
      h-[65px] w-full
      bg-slate-900
      px-8
      rounded-3xl
      shadow-2xl
      flex items-center justify-between
    "
  >
    <!-- LEFT : 금액 / 수량 -->
    <div class="flex items-center gap-6">
      <div>
        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
          Total Amount
        </p>
        <p class="text-2xl font-black text-green-400">
          {{ cartStore.estimatedTotal.toLocaleString() }}원
        </p>
      </div>

      <div class="h-8 w-px bg-slate-700"></div>

      <div>
        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
          Items
        </p>
        <p class="text-xl font-bold text-white">
          {{ cartStore.totalQuantity }}개
        </p>
      </div>
    </div>

    <!-- RIGHT : 결제 버튼 -->
    <button
      class="
        px-8 py-2.5
        bg-green-400 text-slate-900
        rounded-xl
        font-bold text-base
        hover:bg-green-300
        active:scale-95
        transition-all
        shadow-md
      "
    >
      결제하기
    </button>
  </div>
</template>
