import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/api/axios";

export const useCartStore = defineStore("cart", () => {
  /* =========================
   * 1. State
   * ========================= */
  const cartItems = ref([]);
  const cartSession = ref(null); // 세션 정보 (status 등)

  /* =========================
   * 2. Getters
   * ========================= */

  // 예상 총 금액
  const estimatedTotal = computed(() => {
    return cartItems.value.reduce((sum, item) => {
      return sum + item.unit_price * item.quantity;
    }, 0);
  });

  // 전체 수량
  const totalQuantity = computed(() => {
    return cartItems.value.reduce((sum, item) => sum + item.quantity, 0);
  });

  /* =========================
   * 3. Actions (API 연동)
   * ========================= */

  /**
   * 🔹 카트 세션 조회 (아이템 포함)
   * GET /api/carts/{session_id}
   */
  const fetchCartSession = async (cartSessionId) => {
    const res = await api.get(`/api/carts/${cartSessionId}`);

    /*
      예상 응답 형태
      {
        cart_session_id: 1,
        status: "ACTIVE",
        items: [
          {
            cart_item_id: 1,
            product_id: 3,
            name: "스파게티면 500g",
            unit_price: 3200,
            quantity: 1,
            image_url: "...",
            status: "verified"
          }
        ]
      }
    */
    cartSession.value = res.data;
    cartItems.value = res.data.items ?? [];
  };

  /**
   * 🔹 상품 수량 변경
   * PATCH /api/carts/items/{cart_item_id}
   */
  const updateQuantity = async (cartItemId, newQuantity) => {
    if (newQuantity < 1) return;

    await api.patch(`/api/carts/items/${cartItemId}`, {
      quantity: newQuantity,
    });

    const item = cartItems.value.find(
      (i) => i.cart_item_id === cartItemId
    );
    if (item) item.quantity = newQuantity;
  };

  /**
   * 🔹 상품 제거
   * DELETE /api/carts/items/{cart_item_id}
   */
  const removeItem = async (cartItemId) => {
    await api.delete(`/api/carts/items/${cartItemId}`);

    cartItems.value = cartItems.value.filter(
      (i) => i.cart_item_id !== cartItemId
    );
  };

  /**
   * 🔹 무게 검증
   * POST /api/carts/weight/validate
   */
  const validateWeight = async (measuredWeight) => {
    const res = await api.post("/api/carts/weight/validate", {
      measured_weight: measuredWeight,
    });
    return res.data; // { is_valid, diff_weight, ... }
  };

  /**
   * 🔹 결제 요청
   * POST /api/carts/checkout
   */
  const checkout = async () => {
    await api.post("/api/carts/checkout");
  };

  /**
   * 🔹 카트 세션 취소
   * POST /api/carts/cancel
   */
  const cancelCart = async () => {
    await api.post("/api/carts/cancel");
    cartItems.value = [];
    cartSession.value = null;
  };

  return {
    // state
    cartItems,
    cartSession,

    // getters
    estimatedTotal,
    totalQuantity,

    // actions
    fetchCartSession,
    updateQuantity,
    removeItem,
    validateWeight,
    checkout,
    cancelCart,
  };
});
