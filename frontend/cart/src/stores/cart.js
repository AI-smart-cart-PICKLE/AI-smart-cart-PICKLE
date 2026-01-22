import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  // 1. 상태 (State): 장바구니 상품 목록
  const cartItems = ref([
    {
      id: 1,
      name: 'Organic Strawberries',
      price: 6.50,
      quantity: 1,
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDqvyouVvrG65ig1GMysmJo04PsNi0R-4gm5eOWGRPucmZoaZPJnZny6a8diKHwrMJjrspvvlxb5Cxdp5lAf9h6RSZkiC4_WXD4i4ejyDAxfHYYOPyG08quB3CAhgfUmzZ-dh0ajkvrvAecxPi-2b1eK5PDzEANs2hHZuXN1EM0JczpsM7pjV7-DjKF_N-gjFaYX0exngU9z5fCbqGFgXhek24UCZCZPDiYEHBaX1RizYBZr0sem1TnwDniGQLvdXDeRHetDkC-dbw',
      status: 'verified' // verified or pending
    },
    {
      id: 2,
      name: 'Hass Avocado (Large)',
      price: 1.45, // 개당 가격 가정
      quantity: 2,
      image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuALUTM0bqCKVEuPd1ARB0jxIDEVV902597sb7DBGDzEx5PVCwysE9krdPyCt3_bw099InJ0WDyroEZahpaNyz5WEkrDXRxOzqzc4u47xFGQ-8lv4JUcynbQKbY49kMAQkndG-bndcSwsEi0RhSjPnswX33ocO9EY7MqKsaZyuQAxxqaPrks_Di5ZdbgfxSkIw37AycsCydTg-wBCD830K7Z9fw7EtssliF1rKWiQqWlbXTTiuP2XAmtnA0AUxVI0Zmu1QBZuY568bk',
      status: 'pending'
    },
    // ... 나머지 아이템들도 여기에 추가
  ])

  // 2. 계산된 값 (Getters): 총 가격 자동 계산
  const estimatedTotal = computed(() => {
    return cartItems.value.reduce((sum, item) => {
        // 여기서 (가격 x 수량)을 계산해서 합칩니다!
        return sum + (item.price * item.quantity) 
    }, 0).toFixed(2) // 소수점 2자리까지 표시
    })

    // 전체 수량 합계
  const totalQuantity = computed(() => {
    return cartItems.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  // 3. 기능 (Actions)
  const increment = (id) => {
    const item = cartItems.value.find(i => i.id === id)
    if (item) item.quantity++
  }

  const decrement = (id) => {
    const item = cartItems.value.find(i => i.id === id)
    if (item && item.quantity > 1) item.quantity--
  }

  const removeItem = (id) => {
    cartItems.value = cartItems.value.filter(i => i.id !== id)
  }

  return { cartItems, estimatedTotal, totalQuantity, increment, decrement, removeItem }
})
