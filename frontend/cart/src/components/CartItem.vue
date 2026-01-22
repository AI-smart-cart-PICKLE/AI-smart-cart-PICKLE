<script setup>
import { useCartStore } from '@/stores/cart'

// 부모에게서 item 정보를 받음
const props = defineProps({
  item: Object
})

const store = useCartStore()
</script>

<template>
  <div class="flex items-center gap-4 p-4 bg-white border border-slate-100 rounded-2xl shadow-sm relative overflow-hidden group mb-4">
    <img :src="item.image" :alt="item.name" class="w-16 h-16 rounded-xl object-cover shrink-0" />
    
    <div class="flex-1 min-w-0">
      <div class="flex justify-between items-start mb-1">
        <h3 class="font-bold text-sm truncate pr-2">{{ item.name }}</h3>
        
        <div v-if="item.status === 'verified'" class="flex items-center gap-1 shrink-0 bg-primary/10 px-2 py-0.5 rounded text-primary">
          <span class="material-symbols-outlined text-sm font-bold">check_circle</span>
          <span class="text-[9px] font-black uppercase tracking-tighter">Verified</span>
        </div>
        <div v-else class="flex items-center gap-1 shrink-0 bg-amber-400/10 px-2 py-0.5 rounded text-amber-500">
           <span class="material-symbols-outlined text-sm font-bold">sync</span>
           <span class="text-[9px] font-black uppercase tracking-tighter">Pending</span>
        </div>
      </div>

      <div class="flex items-center justify-between mt-2">
        <div class="flex items-center gap-3 bg-white border border-slate-200 p-1 rounded-xl shadow-sm">
          <button @click="store.decrement(item.id)" class="w-10 h-10 flex items-center justify-center bg-slate-50 rounded-lg text-slate-600 hover:bg-slate-100">
            <span class="material-icons-round text-xl">remove</span>
          </button>
          <span class="text-lg font-extrabold w-6 text-center">{{ item.quantity }}</span>
          <button @click="store.increment(item.id)" class="w-10 h-10 flex items-center justify-center bg-slate-50 rounded-lg text-slate-600 hover:bg-slate-100">
            <span class="material-icons-round text-xl">add</span>
          </button>
        </div>
        
        <div class="flex items-center gap-4">
          <span class="text-slate-900 font-bold text-lg">${{ (item.price * item.quantity).toFixed(2) }}</span>
          <button @click="store.removeItem(item.id)" class="w-10 h-10 flex items-center justify-center bg-red-50 text-red-500 rounded-xl hover:bg-red-500 hover:text-white transition-colors">
            <span class="material-icons-round text-xl">delete</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>