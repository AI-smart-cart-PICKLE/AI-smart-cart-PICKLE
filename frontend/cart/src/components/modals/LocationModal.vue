<script setup>
const props = defineProps({
  isOpen: Boolean,
  item: Object
})

const emit = defineEmits(['close'])

// [지도 설정] Aisle 번호와 화면에 표시할 이름 매칭
const zones = [
  { aisle: 1, name: 'Produce', label: '청과/채소' },
  { aisle: 2, name: 'Bakery', label: '베이커리' },
  { aisle: 3, name: 'Meat', label: '정육/축산' },
  { aisle: 4, name: 'Dairy', label: '유제품/계란' },
  { aisle: 5, name: 'Drinks', label: '음료/주류' },
  { aisle: 6, name: 'Frozen', label: '냉동식품' }
]

// 현재 아이템이 해당 구역인지 확인
const isCurrentZone = (zoneAisle) => {
  return props.item?.aisle === zoneAisle
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black/40 backdrop-blur-[2px] z-50 flex items-center justify-center transition-opacity">
    
    <div class="bg-white w-[960px] h-[520px] rounded-[2rem] shadow-2xl flex flex-col overflow-hidden animate-pop relative">
      
      <button @click="emit('close')" class="absolute top-5 right-5 text-slate-400 hover:text-slate-600 transition-colors z-20">
        <span class="material-icons-round text-2xl">close</span>
      </button>

      <div class="px-8 pt-8 pb-4">
        <h1 class="text-2xl font-bold text-slate-800 tracking-tight">위치 확인</h1>
        <p class="text-primary font-bold text-base mt-1">
          {{ item.section }} (Aisle {{ item.aisle }})
        </p>
      </div>

      <div class="flex-1 flex px-8 pb-8 gap-6">
        
        <div class="w-[34%] bg-white border border-slate-100 rounded-3xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.03)] flex flex-col justify-between">
          <div>
            <div class="relative w-full aspect-[4/3] rounded-xl overflow-hidden mb-4 bg-slate-50">
              <img :src="item.image" class="w-full h-full object-cover" alt="Product Image" />
              <div class="absolute top-2 left-2 bg-black/70 backdrop-blur-md px-2 py-1 rounded-md">
                <span class="text-white text-[10px] font-medium">실시간 재고 있음</span>
              </div>
            </div>
            
            <h2 class="text-xl font-bold text-slate-800 leading-tight mb-1">{{ item.name }}</h2>
            <p class="text-slate-500 text-xs">아보카도와 찰떡궁합 (AI 추천)</p>
          </div>

          <div class="bg-green-50 rounded-xl p-3 flex items-center gap-3 mt-3">
            <div class="w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-sm text-primary shrink-0">
              <span class="material-icons-round text-lg">place</span>
            </div>
            <div>
              <p class="text-primary font-bold text-base leading-none">Aisle {{ item.aisle }}</p>
              <p class="text-slate-500 text-xs mt-0.5">{{ item.section }} 코너</p>
            </div>
          </div>
        </div>

        <div class="w-[66%] bg-slate-50 rounded-3xl p-5 border border-slate-100 relative">
          <div class="grid grid-cols-3 grid-rows-2 h-full gap-3">
            
            <div 
              v-for="zone in zones" 
              :key="zone.aisle"
              class="relative rounded-2xl border transition-all duration-300 flex flex-col justify-center px-4"
              :class="[
                isCurrentZone(zone.aisle) 
                  ? 'bg-white border-primary border-dashed shadow-md z-10 scale-[1.01]' 
                  : 'bg-transparent border-transparent hover:bg-white hover:border-slate-200'
              ]"
            >
              <p class="text-[10px] text-slate-400 font-bold uppercase mb-0.5">Aisle {{ zone.aisle }}</p>
              <h3 
                class="text-lg font-bold leading-tight"
                :class="isCurrentZone(zone.aisle) ? 'text-slate-800' : 'text-slate-400'"
              >
                {{ zone.name }}
              </h3>
              <p class="text-xs text-slate-400 font-medium">{{ zone.label }}</p>

              <div v-if="isCurrentZone(zone.aisle)" class="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-green-100 text-primary rounded-full flex items-center justify-center animate-bounce-custom shadow-sm">
                <span class="material-icons-round text-xl">shopping_basket</span>
              </div>
            </div>

            <div class="absolute bottom-5 -right-5 rotate-90 text-slate-300 text-[9px] font-bold tracking-widest">
              ENTRANCE
            </div>
          </div>
        </div>

      </div>

      <div class="absolute bottom-5 left-0 right-0 flex justify-center pointer-events-none">
        <button 
          @click="emit('close')" 
          class="pointer-events-auto bg-primary hover:bg-[#158f40] text-white text-base font-bold py-2.5 px-12 rounded-2xl shadow-[0_8px_20px_rgba(84,184,126,0.3)] transition-transform active:scale-95 flex items-center gap-2"
        >
          닫기 <span class="material-icons-round text-lg">arrow_forward</span>
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.border-dashed {
  border-width: 2px;
  border-style: dashed;
}

.animate-pop {
  animation: popUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes popUp {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.animate-bounce-custom {
  animation: bounceSoft 2s infinite;
}

@keyframes bounceSoft {
  0%, 100% { transform: translateY(-50%) scale(1); }
  50% { transform: translateY(-58%) scale(1.05); }
}
</style>