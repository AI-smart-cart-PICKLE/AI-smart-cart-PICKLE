<template>
  <div class="pair-container">
    <div class="content-wrapper">
      <div class="text-center">
        <h1 class="main-title">Pickle Smart Cart</h1>
        <p class="sub-title">카트 연동을 위해 QR 코드를 스캔하세요</p>
      </div>

      <!-- QR 코드 영역 (Canvas 기반) -->
      <div class="qr-section">
        <div class="qr-card">
          <div class="qr-white-box">
            <canvas ref="qrCanvas"></canvas>
            <div v-if="loading" class="loading-text">QR 생성 중...</div>
          </div>
        </div>
      </div>

      <div class="guide-section">
        <p class="guide-text">
          모바일 앱의 <b>'QR 스캔'</b> 메뉴를 열고<br/>
          위의 코드를 인식시켜 주세요.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const qrCanvas = ref(null)
const loading = ref(true)
const deviceCode = 'CART-DEVICE-001'

// 라이브러리 없이 QR 생성을 위해 CDN 스크립트 동적 로드
const loadQRCodeLib = () => {
  return new Promise((resolve) => {
    if (window.QRious) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js'
    script.onload = resolve
    document.head.appendChild(script)
  })
}

onMounted(async () => {
  await loadQRCodeLib()
  
  if (window.QRious && qrCanvas.value) {
    new window.QRious({
      element: qrCanvas.value,
      value: deviceCode,
      size: 250,
      level: 'H'
    })
    loading.value = false
  }
})
</script>

<style scoped>
.pair-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 536px;
  background-color: #f8fafc;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.main-title {
  font-size: 40px;
  font-weight: 900;
  color: #0f172a;
}

.sub-title {
  font-size: 18px;
  font-weight: 700;
  color: #64748b;
}

.qr-section {
  padding: 24px;
  background-color: #ffffff;
  border-radius: 40px;
  border: 4px solid #4ade80;
  box-shadow: 0 25px 50px -12px rgba(74, 222, 128, 0.15);
}

.qr-white-box {
  background-color: #ffffff;
  padding: 10px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 250px;
  height: 250px;
}

.guide-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.guide-text {
  text-align: center;
  color: #94a3b8;
}

.loading-text {
  color: #94a3b8;
  font-size: 14px;
}
</style>
