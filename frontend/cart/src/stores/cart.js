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

    cartSession.value = {
      cart_session_id: res.data.cart_session_id,
      status: res.data.status,
      device_code: res.data.device_code,
    };

    cartItems.value = (res.data.items ?? []).map((item) => ({
      cart_item_id: item.cart_item_id,
      product_id: item.product?.product_id,

      // 프론트 표준 필드
      product_name: item.product?.name,
      unit_price: item.unit_price,
      quantity: item.quantity,
      image_url: item.product?.image_url,

      // 검증 상태 가공 (임시로 true 처리, 필요시 백엔드 스키마 확장 필요)
      is_verified: true,
    }));
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
 * 🔹 바코드로 상품 추가
 * POST /api/carts/items/barcode
 */
const addItemByBarcode = async (barcode) => {
  if (!cartSession.value?.cart_session_id) {
    throw new Error("카트 세션이 없습니다.")
  }

  // 1️ 바코드 → 상품 조회
  const productRes = await api.get(`/api/products/barcode/${barcode}`)
  const product = productRes.data

  // 2️ 장바구니에 추가
  await api.post(
    `/api/carts/${cartSession.value.cart_session_id}/items`,
    {
      product_id: product.product_id,
      quantity: 1,
    }
  )

  // 3️⃣ 다시 조회해서 UI 동기화
  await fetchCartSession(cartSession.value.cart_session_id)
}


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
    addItemByBarcode,
  };
});
