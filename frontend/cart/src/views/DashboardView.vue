<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import CartItem from '@/components/CartItem.vue'
import RecoCard from '@/components/RecoCard.vue'
import LocationModal from '@/components/modals/LocationModal.vue'

const store = useCartStore()

// [추가 2] 상품 데이터에 위치 정보 추가 (aisle 1~6 사이로 설정)
const recoItems = ref([
  { id: 1, name: 'Artisan Sourdough', price: 5.40, desc: '아보카도와 찰떡궁합', image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDdVuOJ2W0rKfp2mO6-KqyeJNXuAfw6HeCkgJav3Qmzz_SIP63wGL6nAVzA1i8q4EG1k8R17nhamrZK4TB4KyRYfwmT8z2wnd8UeNOLlUsF0ZBt2QjnyweplwLAx0dJ-ZJChJXgQ7cg3qGIDTY68e37q8SL3J8GJOA5Uk0S-pk7KCAO2wsn1sQQ1iqjiDvM_OYXjLsSdlbXssifrmaH_c_8pxOhgmLpJ_RXQk_MaNCYo61fD0tjCaymGemBxV3BPNrjY5gLf-sK8sI', aisle: 2, section: 'Bakery' },
  { id: 2, name: 'Honey Nut Granola', price: 7.20, desc: '우유와 함께 드세요', image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuD6SUiyewPt0rrS8Bo7vHihzHahZk1UOyBLa_QDISYfaRHXdy0aUULdkMT9qmRINjHEoAdtb4GMFD0aVvm8at9v4WGvRy6uMbm6kHC0zIylmM4T9R4KlHMsfYqhanJYd4ZUKiHayni4_j5kpO6syXGWIRlyPOnIPWY4Dfhd1rHWxfagEE8yCrW3Jupoz8kjk-RyB5KiyIhgDPlOMLzp7B_Ijt4F895ftUy_DHb2OJZiJnFLSN_efrgr_KKVLLFlDQG-NBUS_1ct0bY', aisle: 1, section: 'Produce' },
  { id: 3, name: 'Plain Greek Yogurt', price: 4.50, desc: '딸기 토핑으로 최고', image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuA8YFcHdxN79p7rnEjSus7l0HSLBEmhspiYDWcB3YYsPoEsut4zouP8UJvBfywY5-ydlvqtXFTqJWCW4LJWhMhwgN8wZLseSLLj_47qEwyWY0a8xnINdBRSpcwDGjUArufqsdpBCEfGqovThYS_Fq9DhnTV4D-qCUKsyOtUjJ4hVhUesnjqgYdclQvRLk9v-lQmTmue6_s9CLAWJKHQPij_KK8IJQVoHWJZYJ1WXu-D8g_dPI3kb0fVu3SL6aVb29sRpyhUDblFI04', aisle: 4, section: 'Dairy' },
  { id: 4, name: 'Pure Maple Syrup', price: 12.50, desc: '팬케이크 필수품', image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCFfmvGaADMsJCqkwl_C3ICLVohe49W8sCZeSWY-qU0MUGV8LQkWfg1BlSLuJebxnjn1wFn31rPUmkuzjet1UNqlytXDY2_sx7493niSW97R374BCCgwNHnJ5Z3AzjI_IU8dC4XJ-19mD32ROXeN7HgN4RUZxdhR45KFO8NOL78gjMGY4xB1y0OPsv-7wEj0wgLcQ9HuGMfyuhYwnK6WM7rO-k6wZrer8_ZmE6cecOxaVYEVM0XBahHNpKojWlRZjOES6YjB8Yy6Lg', aisle: 6, section: 'Grocery' },
])

// [추가 3] 모달 상태 관리 변수
const isLocModalOpen = ref(false)
const selectedRecoItem = ref({}) // 현재 선택된 상품 정보 저장

// [추가 4] 모달 열기 함수
const openLocationModal = (item) => {
  selectedRecoItem.value = item
  isLocModalOpen.value = true
}

const showCamera = ref(false)
</script>

<template>
  <main class="flex h-[534px]">
    <section class="w-1/2 flex flex-col border-r border-slate-100">
        <div class="p-6 flex items-center justify-between bg-white">
            <div>
              <h2 class="text-lg font-bold flex items-center gap-2">
                <span class="material-icons-round text-primary">shopping_cart</span>
                담은 상품 <span class="text-primary ml-1">({{ store.totalQuantity }})</span>
              </h2>
              <p class="text-xs text-slate-400 font-medium">실시간 무게 감지 및 스캔 중</p>
            </div>
            <div class="text-right">
              <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Estimated Total</p>
              <span class="text-2xl text-slate-900 font-extrabold tracking-tight">${{ store.estimatedTotal }}</span>
            </div>
          </div>
          <div class="flex-1 overflow-y-auto px-6 pb-6 custom-scrollbar">
            <CartItem v-for="item in store.cartItems" :key="item.id" :item="item" />
          </div>
          <div class="p-6 bg-white border-t border-slate-100">
            <button class="w-full bg-slate-900 hover:bg-black text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-3 shadow-lg active:scale-[0.98] transition-transform">
              <span class="material-icons-round">payment</span>
              결제하기 (${{ store.estimatedTotal }})
            </button>
          </div>
    </section>

    <section class="w-1/2 flex flex-col p-6 gap-6 bg-slate-50/30">
      <div class="flex flex-col flex-1 min-h-0">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-black flex items-center gap-2 uppercase tracking-widest text-slate-600">
            <span class="material-symbols-outlined text-primary text-xl font-bold">star</span>
            Recommended Ingredients
          </h3>
          <span class="text-[10px] font-bold text-primary bg-primary/10 px-2 py-1 rounded">AI 맞춤 추천</span>
        </div>
        
        <div class="grid grid-cols-2 gap-4 overflow-y-auto flex-1 custom-scrollbar pr-1">
          <RecoCard 
            v-for="reco in recoItems" 
            :key="reco.id" 
            :item="reco" 
            @open-location="openLocationModal" 
          />
        </div>
      </div>

      <div class="grid grid-cols-3 gap-4 h-32 mt-auto">
        <button @click="showCamera = true" class="flex flex-col items-center justify-center gap-3 bg-white border-2 border-primary/20 hover:border-primary rounded-3xl transition-all shadow-sm hover:shadow-lg group active:scale-[0.98]">
           <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-colors">
            <span class="material-icons-round text-3xl">videocam</span>
          </div>
           <div class="text-center">
            <span class="block text-sm font-bold text-slate-800">AI Camera</span>
            <span class="block text-[10px] font-bold text-slate-400 uppercase">카메라 보기</span>
          </div>
        </button>
        <button class="flex flex-col items-center justify-center gap-3 bg-white border-2 border-primary/20 hover:border-primary rounded-3xl transition-all shadow-sm hover:shadow-lg group active:scale-[0.98]">
           <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-colors">
            <span class="material-symbols-outlined text-3xl font-bold">barcode_scanner</span>
          </div>
           <div class="text-center">
            <span class="block text-sm font-bold text-slate-800">Manual Add</span>
            <span class="block text-[10px] font-bold text-slate-400 uppercase">상품 추가</span>
          </div>
        </button>
        <button class="flex flex-col items-center justify-center gap-3 bg-white border-2 border-primary/20 hover:border-primary rounded-3xl transition-all shadow-sm hover:shadow-lg group active:scale-[0.98]">
           <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-colors">
            <span class="material-icons-round text-3xl">mic</span>
          </div>
           <div class="text-center">
            <span class="block text-sm font-bold text-slate-800">Voice Search</span>
            <span class="block text-[10px] font-bold text-slate-400 uppercase">음성 검색</span>
          </div>
        </button>
      </div>
    </section>
  </main>
  
  <LocationModal 
    :isOpen="isLocModalOpen" 
    :item="selectedRecoItem"
    @close="isLocModalOpen = false"
  />

  <div v-if="showCamera" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center text-white">
      <div class="bg-slate-900 p-8 rounded-2xl">
          <h2 class="text-xl font-bold mb-4">AI Vision Feed</h2>
          <button @click="showCamera = false" class="bg-primary px-4 py-2 rounded">닫기</button>
      </div>
  </div>
</template>