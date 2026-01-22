<script setup>
// 특별한 로직이 없으므로 비워둡니다.
</script>

<template>
  <header class="h-16 px-8 flex items-center justify-between bg-white border-b border-slate-100 sticky top-0 z-10">
    <div class="flex items-center gap-3">
      <div class="bg-primary p-2 rounded-xl">
        <span class="material-icons-round text-white">shopping_basket</span>
      </div>
      <div>
        <h1 class="text-xl font-extrabold tracking-tight">Pickle <span class="text-primary text-sm font-bold ml-1 uppercase">Smart Dashboard</span></h1>
      </div>
    </div>

    <div class="flex items-center gap-8">
      <div class="flex flex-col items-end">
        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none">Cart ID</span>
        <span class="text-sm font-bold text-slate-700">PKL-0428-A</span>
      </div>
      <div class="h-8 w-px bg-slate-100"></div>
      <div class="flex items-center gap-3">
        <div class="text-right">
          <p class="text-xs font-bold text-slate-900 leading-none">Sarah Kim</p>
          <p class="text-[10px] text-primary font-bold">Premium Member</p>
        </div>
        <img alt="User Profile" class="w-10 h-10 rounded-full border-2 border-primary/20" src="../../src/assets/pickle-logo.png"/>
      </div>
    </div>
  </header>
</template>