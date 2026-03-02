<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
      <p class="text-sm font-medium text-slate-500 mb-1">Current Load</p>
      <div class="flex items-baseline gap-2">
        <h2 class="text-3xl font-bold text-slate-900">{{ value || '0.00' }}</h2>
        <span class="text-slate-400 font-medium">kWh</span>
      </div>
      <div class="mt-4 flex items-center gap-2">
        <span :class="['w-2 h-2 rounded-full', value > 50 ? 'bg-amber-500' : 'bg-emerald-500']"></span>
        <span class="text-[10px] font-bold uppercase tracking-tight" :class="value > 50 ? 'text-amber-600' : 'text-emerald-600'">
          {{ value > 50 ? 'High Demand' : 'Optimal' }}
        </span>
      </div>
    </div>

    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
      <p class="text-sm font-medium text-slate-500 mb-1">Peak Today</p>
      <div class="flex items-baseline gap-2">
        <h2 class="text-3xl font-bold text-slate-700">{{ peak.toFixed(2) }}</h2>
        <span class="text-slate-400 font-medium">kWh</span>
      </div>
    </div>

    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
      <div class="bg-emerald-100 p-3 rounded-xl text-xl"></div>
      <div>
        <p class="text-sm font-bold text-slate-800">System Online</p>
        <p class="text-xs text-slate-400 font-medium leading-tight">Kafka & Redis stream active</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  value: Number,
  peak: Number
});
</script>