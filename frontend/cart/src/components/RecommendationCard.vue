<script setup>
defineProps({
  item: Object // 부모에게서 상품 정보를 받음
})

const emit = defineEmits(['open-location'])
</script>

<template>
  <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex flex-col gap-3 group hover:border-primary transition-all">
    <div class="flex gap-3">
      <img :src="item.image" :alt="item.name" class="w-14 h-14 rounded-xl object-cover" />
      <div class="flex-1 min-w-0">
        <h5 class="text-sm font-bold truncate">{{ item.name }}</h5>
        <p class="text-primary font-bold text-sm">${{ item.price }}</p>
        <p class="text-[10px] text-slate-400 mt-1">{{ item.desc }}</p>
      </div>
    </div>
    <button 
      @click="emit('open-location', item)" 
      class="w-full flex items-center justify-center gap-2 bg-primary/10 hover:bg-primary text-primary hover:text-white text-xs font-bold py-2 rounded-xl transition-all"
    >
      <span class="material-symbols-outlined text-sm">location_on</span>
      위치 보기
    </button>
  </div>
</template>