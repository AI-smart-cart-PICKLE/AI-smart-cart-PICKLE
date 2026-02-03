<script setup>
import { computed } from 'vue'
import { useCartStore } from '@/stores/cart'

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})

const cartStore = useCartStore()

/* -----------------------
   상태 계산
----------------------- */
const isPending = computed(() => !props.item.is_verified)

/* -----------------------
   수량 조절
----------------------- */
const increase = () => {
  if (isPending.value) return
  cartStore.updateQuantity(props.item.cart_item_id, props.item.quantity + 1)
}

const decrease = () => {
  if (isPending.value) return
  if (props.item.quantity <= 1) return
  cartStore.updateQuantity(props.item.cart_item_id, props.item.quantity - 1)
}

const remove = () => {
  cartStore.removeItem(props.item.cart_item_id)
}
</script>

<template>
  <div class="flex items-center justify-between p-3 bg-white rounded-2xl border">

    <!-- LEFT : 상품 정보 -->
    <div class="flex items-center gap-3">
      <img
        v-if="item.image_url"
        :src="item.image_url"
        class="w-12 h-12 rounded-xl object-cover"
      />

      <div>
        <!-- ✅ 상품명 -->
        <p class="font-bold text-slate-800 text-sm">
          {{ item.product_name }}
        </p>

        <!-- 검증 상태 -->
        <span
          class="text-[10px] px-2 py-0.5 rounded-full"
          :class="item.is_verified
            ? 'bg-indigo-50 text-indigo-600 font-bold'
            : 'bg-yellow-100 text-yellow-600 font-bold'"
        >
          {{ item.is_verified ? 'VERIFIED' : 'PENDING' }}
        </span>
      </div>
    </div>

    <!-- RIGHT : 수량 / 가격 / 삭제 -->
    <div class="flex items-center gap-4">

      <!-- 수량 조절 -->
      <div class="flex items-center gap-2">
        <button
          @click="decrease"
          class="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center font-bold"
        >
          −
        </button>

        <span class="font-bold w-5 text-center text-sm">
          {{ item.quantity }}
        </span>

        <button
          @click="increase"
          class="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center font-bold"
        >
          +
        </button>
      </div>

      <!-- 가격 -->
      <p class="font-bold text-slate-700 w-20 text-right text-sm">
        {{ (item.unit_price * item.quantity).toLocaleString() }}원
      </p>

      <!-- 삭제 -->
      <button
        @click="remove"
        class="text-red-400 hover:text-red-600 p-1"
      >
        🗑
      </button>
    </div>
  </div>
</template>
