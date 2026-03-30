<template>
  <aside class="w-52 shrink-0 bg-white border-r border-slate-200 flex flex-col py-5 px-3 gap-1">
    <button
      v-for="item in navItems"
      :key="item.view"
      @click="$emit('update:modelValue', item.view)"
      :class="[
        'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all w-full text-left',
        modelValue === item.view
          ? 'bg-emerald-50 text-emerald-700 font-semibold'
          : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'
      ]"
    >
      <component :is="item.icon" :size="17" class="shrink-0" />
      {{ item.label }}
    </button>
  </aside>
</template>

<script setup>
import { LayoutDashboard, Building2, Home, Cpu, Sliders } from 'lucide-vue-next';

defineProps(['modelValue']);
defineEmits(['update:modelValue']);

const navItems = [
  { view: 'dashboard',  label: 'Dashboard',  icon: LayoutDashboard },
  { view: 'buildings',  label: 'Buildings',  icon: Building2 },
  { view: 'units',      label: 'Units',      icon: Home },
  { view: 'sensors',    label: 'Sensors',    icon: Cpu },
  { view: 'thresholds', label: 'Thresholds', icon: Sliders },
];
</script>
