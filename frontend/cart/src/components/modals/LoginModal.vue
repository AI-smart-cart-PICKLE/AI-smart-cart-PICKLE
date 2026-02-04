<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { useRouter } from 'vue-router'

const emit = defineEmits(['close'])

const authStore = useAuthStore()
const cartStore = useCartStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

const login = async () => {
  errorMsg.value = ''
  loading.value = true

  try {
    /**
     * 1️⃣ 로그인 (토큰 저장 + me 조회)
     */
    try {
      await authStore.login(email.value, password.value)
    } catch (e) {
      console.error("Auth Error:", e)
      throw new Error(e.response?.data?.detail || '이메일 또는 비밀번호가 올바르지 않습니다.')
    }

    /**
     * 2️⃣ 카트 세션 생성
     *  - 성공 시 localStorage에 cart_session_id 저장
     */
    try {
      const res = await cartStore.createCartSession()
      localStorage.setItem('cart_session_id', res.cart_session_id)
      // 🔥 스토어 상태 즉시 동기화
      await cartStore.fetchCartSession(res.cart_session_id)
    } catch (e) {
      console.error("Cart Session Error:", e)
      throw new Error('카트 세션을 생성하는 중 오류가 발생했습니다.')
    }

    /**
     * 3️⃣ 모달 닫기 + 대시보드 이동
     */
    emit('close')
    router.replace('/') // push ❌ replace ⭕

  } catch (e) {
    console.error(e)
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center
           bg-slate-900/50 backdrop-blur-sm"
  >
    <div
      class="bg-white w-full max-w-md p-10 rounded-[40px]
             shadow-2xl relative"
    >
      <!-- 닫기 -->
      <button
        @click="emit('close')"
        class="absolute top-6 right-6 p-2 rounded-full
               hover:bg-slate-50"
      >
        <span class="material-icons-round text-slate-400">close</span>
      </button>

      <!-- 타이틀 -->
      <div class="text-center mb-8">
        <h3 class="text-3xl font-black text-slate-800 mb-2">
          Welcome Back
        </h3>
        <p class="text-slate-400 font-medium">
          테스트 계정으로 로그인하세요
        </p>
      </div>

      <!-- 입력 -->
      <div class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-400 mb-2 ml-1">
            Email
          </label>
          <input
            v-model="email"
            type="email"
            placeholder="test@test.com"
            class="w-full px-6 py-4 bg-slate-50
                   rounded-2xl font-bold"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-400 mb-2 ml-1">
            Password
          </label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            class="w-full px-6 py-4 bg-slate-50
                   rounded-2xl font-bold"
            @keyup.enter="login"
          />
        </div>

        <!-- 에러 -->
        <p
          v-if="errorMsg"
          class="text-red-500 text-sm font-bold text-center"
        >
          {{ errorMsg }}
        </p>

        <!-- 버튼 -->
        <button
          @click="login"
          :disabled="loading"
          class="w-full py-5 bg-primary text-white
                 rounded-[24px] font-black text-lg
                 disabled:opacity-50"
        >
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-primary {
  background-color: #4ade80;
}
</style>
