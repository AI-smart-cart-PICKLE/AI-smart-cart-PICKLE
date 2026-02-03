<script setup>
defineProps({
  recipe: Object
})
</script>

<template>
  <div
    class="bg-slate-100 border rounded-xl p-5
           hover:border-green-400 cursor-pointer transition"
  >
    <!-- 이미지 -->
    <div class="h-20 bg-slate-200 rounded-lg mb-1 overflow-hidden">
      <img
        v-if="recipe.image_url"
        :src="recipe.image_url"
        class="w-full h-full object-cover"
      />
      <div
        v-else
        class="w-full h-full flex items-center justify-center text-slate-400 text-xs"
      >
        이미지 없음
      </div>
    </div>

    <!-- 제목 -->
    <h3 class="font-semibold text-xs text-slate-800 truncate text-center">
      {{ recipe.title }}
    </h3>
  </div>
</template>
