<script setup>
defineProps({
  item: Object
});
</script>

<template>
  <div>
    <img :src="item.image_url" />
    <div>{{ item.name }}</div>
    <div>{{ item.unit_price }}원</div>
    <div>수량: {{ item.quantity }}</div>
  </div>
</template>
