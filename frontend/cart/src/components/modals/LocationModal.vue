<!-- LocationModal.vue -->
<template>
  <div class="modal-overlay">
    <div class="modal-content">
      
      <!-- 헤더 -->
      <div class="modal-header">
        <h2>📍 상품 위치 안내</h2>
        <button class="close-x" @click="$emit('close')">✕</button>
      </div>

      <!-- 본문 -->
      <div class="modal-body" v-if="location">
        <p class="location-title">
          위치 : <strong>{{ location.zone_code }}</strong>
        </p>

        <MapModal :highlightZone="location.zone_code" />
      </div>

      <div v-else class="loading">
        위치 정보를 불러오는 중...
      </div>


    </div>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/api/axios'
import MapModal from './MapModal.vue'

const props = defineProps({
  productId: {
    type: Number,
    required: true
  }
})

const location = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await axios.get(
      `/products/${props.productId}/location`
    )
    location.value = res.data
  } catch (error) {
    console.error('❌ 위치 조회 실패', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.modal-content {
  background: #fff;
  width: 100%;
  width: 900px;   
  height: 520px;   
  padding: 20px;
  border-radius: 16px;

  display: flex;
  flex-direction: column;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-x {
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  background: none;
  border: none;
}

.close-x:hover {
  color: #ef4444;
}


.product-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 6px;
}

.location-text {
  margin-bottom: 14px;
}

.loading,
.error {
  margin: 20px 0;
  text-align: center;
}


</style>
