<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

const emit = defineEmits(['close'])
const router = useRouter()

const email = ref('')
const password = ref('')
const errorMsg = ref('')

const login = async () => {
  try {
    // 1. 로그인 요청
    await api.post('/api/auth/login', {
      email: email.value,
      password: password.value,
    })

    // 2. 카트 세션 생성 (또는 기존 세션 로드)
    const res = await api.post('/api/carts/')
    localStorage.setItem('cart_session_id', res.data.cart_session_id)

    // 3. 모달 닫기 및 이동
    emit('close')
    router.push('/')
    
  } catch (e) {
    console.error(e)
    errorMsg.value = e.response?.data?.detail || '로그인에 실패했습니다.'
  }
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
    <div class="bg-white w-full max-w-md p-10 rounded-[40px] shadow-2xl relative animate-in fade-in zoom-in duration-300">
      <button 
        @click="$emit('close')"
        class="absolute top-6 right-6 p-2 rounded-full hover:bg-slate-50 transition-colors"
      >
        <span class="material-icons-round text-slate-400">close</span>
      </button>

      <div class="text-center mb-8">
        <h3 class="text-3xl font-black text-slate-800 mb-2">Welcome Back</h3>
        <p class="text-slate-400 font-medium">테스트 계정으로 로그인하세요</p>
      </div>
      
      <div class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 ml-1">Email</label>
          <input 
            v-model="email" 
            placeholder="test@test.com" 
            class="w-full px-6 py-4 bg-slate-50 border-none rounded-2xl focus:ring-4 focus:ring-primary/20 transition-all font-bold"
          />
        </div>
        
        <div>
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 ml-1">Password</label>
          <input 1
            v-model="password" 
            type="password" 
            placeholder="••••••••" 
            class="w-full px-6 py-4 bg-slate-50 border-none rounded-2xl focus:ring-4 focus:ring-primary/20 transition-all font-bold"
            @keyup.enter="login"
          />
        </div>

        <p v-if="errorMsg" class="text-red-500 text-sm font-bold text-center mt-2">{{ errorMsg }}</p>

        <button 
          @click="login"
          class="w-full py-5 bg-primary text-white rounded-[24px] font-black text-lg shadow-xl shadow-primary/30 hover:scale-[1.02] active:scale-95 transition-all mt-4"
        >
          로그인
        </button>

        <div class="text-center mt-6">
          <p class="text-slate-400 text-sm font-bold">
            계정이 없으신가요? <span class="text-primary cursor-not-allowed">회원가입 (준비중)</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-primary {
  background-color: #4ade80;
}
.text-primary {
  color: #4ade80;
}
.focus\:ring-primary\/20:focus {
  --tw-ring-color: rgb(74 222 128 / 0.2);
}
.shadow-primary\/30 {
  --tw-shadow-color: rgb(74 222 128 / 0.3);
  --tw-shadow: var(--tw-shadow-colored);
}
</style>
