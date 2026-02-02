<template>
  <div class="modal-overlay" @click.self="close">
    <div class="camera-modal">

      <!-- 📷 카메라 -->
      <div ref="cameraContainer" class="camera-view"></div>

      <!-- 안내 -->
      <div v-if="!isConfirming" class="guide-text">
        📷 바코드를 화면 중앙에 맞춰주세요
      </div>

      <!-- ❓ 확인 -->
      <div v-if="isConfirming" class="confirm-overlay">
        <div class="confirm-box">
          <p class="confirm-text">
            <strong>{{ detectedCode }}</strong><br />
            {{ productName || "상품 정보 조회 중..." }}<br /><br />
            이 상품이 맞습니까?
          </p>

          <div class="confirm-actions">
            <button class="yes" @click="confirmYes">네</button>
            <button class="no" @click="confirmNo">아니요</button>
          </div>
        </div>
      </div>

      <!-- ❌ 닫기 -->
      <button class="close-x" @click="close">✕</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue"
import Quagga from "@ericblade/quagga2"
import { useCartStore } from "@/stores/cart"
import api from "@/api/axios"

const emit = defineEmits(["close"])
const cartStore = useCartStore()

const cameraContainer = ref(null)
const detectedCode = ref(null)
const productName = ref(null)
const isConfirming = ref(false)

function close() {
  Quagga.stop()
  emit("close")
}

async function startScanner() {
  await nextTick()

  Quagga.init(
    {
      inputStream: {
        type: "LiveStream",
        target: cameraContainer.value,
        constraints: { facingMode: "environment" },
      },
      decoder: {
        readers: ["ean_reader"],
      },
      locate: true,
    },
    (err) => {
      if (err) {
        console.error(err)
        return
      }
      Quagga.start()
    }
  )

  Quagga.onDetected(onDetected)
}

async function onDetected(result) {
  if (isConfirming.value) return

  detectedCode.value = result.codeResult.code
  isConfirming.value = true

  // 🔍 상품 이름 조회
  try {
    const res = await api.get(`/api/products/barcode/${detectedCode.value}`)
    productName.value = res.data.name
  } catch {
    productName.value = "알 수 없는 상품"
  }
}

async function confirmYes() {
  await cartStore.addItemByBarcode(detectedCode.value)
  close()
}

function confirmNo() {
  detectedCode.value = null
  productName.value = null
  isConfirming.value = false
}

onMounted(startScanner)

onBeforeUnmount(() => {
  Quagga.stop()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.camera-modal {
  position: relative;
  width: 90vw;
  max-width: 900px;
  aspect-ratio: 16 / 9;
  background: white;
  border-radius: 20px;
  overflow: hidden;
}

.camera-view {
  position: absolute;
  inset: 0;
}

.camera-view video,
.camera-view canvas {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.guide-text {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0,0,0,0.6);
  color: white;
  padding: 8px 14px;
  border-radius: 12px;
  z-index: 2;
}

.confirm-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
}

.confirm-box {
  background: white;
  padding: 20px;
  border-radius: 16px;
  text-align: center;
  width: 280px;
}

.confirm-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.confirm-actions .yes {
  background: #22c55e;
  color: white;
  padding: 8px 14px;
  border-radius: 10px;
}

.confirm-actions .no {
  background: #e5e7eb;
  padding: 8px 14px;
  border-radius: 10px;
}

.close-x {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0,0,0,0.6);
  color: white;
  cursor: pointer;
  z-index: 4;
}
</style>
