import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/api/axios";

export const useCartStore = defineStore("cart", () => {
  /* =========================
   * 1. State
   * ========================= */
  const cartItems = ref([]);
  const cartSession = ref({
    cart_session_id: null,
    status: 'ACTIVE',
    device_code: 'CART-DEVICE-001',
  }) // 세션 정보 (status 등)

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
    console.log(`🔍 [DEBUG] fetchCartSession 시작 - ID: ${cartSessionId}`);
    try {
      const res = await api.get(`carts/${cartSessionId}`);
      console.log("✅ [DEBUG] fetchCartSession 성공:", res.data);
      
      // ACTIVE 또는 CHECKOUT_REQUESTED가 아니면 세션이 종료된 것으로 간주
      const validStatuses = ['ACTIVE', 'CHECKOUT_REQUESTED'];
      if (!validStatuses.includes(res.data.status)) {
        cartSession.value = null;
        cartItems.value = [];
        localStorage.removeItem('cart_session_id');
        return;
      }

      cartSession.value = {
        cart_session_id: res.data.cart_session_id,
        status: res.data.status,
        device_code: res.data.device_code ?? 'CART-DEVICE-001',
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
    } catch (e) {
      console.error("❌ [DEBUG] fetchCartSession 실패:", e.response?.status, e.response?.data || e.message);
      // 에러가 나더라도 즉시 지우지 않고 유지하여 리다이렉트 흐름 확인 (테스트용)
      // cartSession.value = null;
      // cartItems.value = [];
      // localStorage.removeItem('cart_session_id');
    }
  };


  /**
   * 🔹 카트 세션 생성 (쇼핑 시작)
   * POST /api/carts/
   */
  const createCartSession = async () => {
    const res = await api.post('carts/')
    
    cartSession.value = {
      cart_session_id: res.data.cart_session_id,
      status: res.data.status,
      device_code: 'CART-DEVICE-001'
    }
    
    // 초기화
    cartItems.value = []
    
    return res.data
  }


  /**
   * 🔹 상품 수량 변경
   * PATCH /api/carts/items/{cart_item_id}
   */
  const updateQuantity = async (cartItemId, newQuantity) => {
    if (newQuantity < 1) return;

    await api.patch(`carts/items/${cartItemId}`, {
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
    await api.delete(`carts/items/${cartItemId}`);

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
  const productRes = await api.get(`products/barcode/${barcode}`)
  const product = productRes.data

  // 2️ 장바구니에 추가
  await api.post(
    `carts/${cartSession.value.cart_session_id}/items`,
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
    const res = await api.post("carts/weight/validate", {
      measured_weight: measuredWeight,
    });
    return res.data; // { is_valid, diff_weight, ... }
  };

  /**
   * 🔹 결제 요청 (모바일 앱으로 결제 신호 전송)
   * POST /api/payments/ready
   */
  const checkout = async () => {
    const sessionId = cartSession.value?.cart_session_id;
    if (!sessionId) throw new Error("결제할 세션이 없습니다.");

    // 1. 결제 준비 요청 (웹 키오스크용은 딥링크를 보내지 않음)
    const res = await api.post(`payments/ready`, {
      cart_session_id: sessionId,
      total_amount: estimatedTotal.value
      // approval_url 등을 보내지 않으면 백엔드가 허용된 도메인 기반의 기본 URL을 사용합니다.
    });
    
    return res.data; // { tid, next_redirect_pc_url, ... }
  };

  /**
 * 🔹 카트 세션 취소
 * POST /api/carts/{session_id}/cancel
 */
const cancelCart = async () => {
  const sessionId = cartSession.value?.cart_session_id;
  if (!sessionId) return;

  try {
    await api.post(`carts/${sessionId}/cancel`);
  } catch (e) {
    console.error("Failed to cancel cart:", e);
  }

  // 로컬 상태를 명확히 비움
  cartItems.value = [];
  cartSession.value = null;
  localStorage.removeItem('cart_session_id');
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
    createCartSession,
  };
});
