<!-- ZoneBox.vue -->
<template>
  <div class="zone-box" :class="{ active }">
    <div class="code">{{ zone.code }}</div>
    <div class="name">{{ zone.name }}</div>
  </div>
</template>

<script setup>
defineProps({
  zone: Object,
  active: Boolean
})
</script>

<style scoped>
.zone-box {
  border: 3px solid #d1d5db;
  border-radius: 14px;
  padding: 14px;
  background: #fff;
  box-shadow: 0 6px 10px rgba(0,0,0,0.05);
}

.zone-box.active {
  background: #bbf7d0;
  border-color: #22c55e;
}


.code {
  font-size: 15px;
}

.name {
  font-size: 11px;
  color: #444;
}
</style>
