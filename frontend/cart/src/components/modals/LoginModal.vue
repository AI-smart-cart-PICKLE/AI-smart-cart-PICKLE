<script setup>
import { ref } from 'vue'
import api from '@/api/axios'

const email = ref('')
const password = ref('')

const login = async () => {
  await api.post('/api/auth/login', {
    email: email.value,
    password: password.value,
  })

  const res = await api.post('/api/carts/')
  localStorage.setItem('cart_session_id', res.data.cart_session_id)

  location.href = '/'
}
</script>

<template>
  <div class="modal">
    <input v-model="email" placeholder="email" />
    <input v-model="password" type="password" placeholder="password" />
    <button @click="login">로그인</button>
  </div>
</template>
