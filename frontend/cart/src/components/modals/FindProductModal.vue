<template>
  <div class="modal-overlay">
    <div class="modal-content">

      <!-- 헤더 -->
      <div class="modal-header">
        <div>
          <h2 class="title">📍 상품 배치도</h2>
        </div>

        <button class="close-x" @click="$emit('close')">✕</button>
      </div>

      <!-- 맵 영역 -->
      <div class="map-wrapper">
        <MapModal :highlightZone="highlightZone" />
      </div>

    </div>
  </div>
</template>


<script setup>
import MapModal from './MapModal.vue'

defineProps({
  highlightZone: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  box-sizing: border-box;
  background: white;

  width: 900px;
  height: 520px;

  padding: 20px 24px 24px;
  border-radius: 20px;
  position: relative;

  display: flex;
  flex-direction: column;
}

/* 헤더 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.title {
  font-size: 20px;
  font-weight: 800;
}

/* 닫기 버튼 */
.close-x {
  font-size: 24px;
  font-weight: bold;
  border: none;
  background: none;
  cursor: pointer;
  line-height: 1;
}

.close-x:hover {
  color: #ef4444;
}

/* 맵 위치 ↓ */
.map-wrapper {
  flex: 1;
  margin-top: 8px;   
}


</style>
