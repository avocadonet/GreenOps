<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">
    <TheHeader />
    <div class="flex flex-1 overflow-hidden" style="height: calc(100vh - 57px)">
      <AppSidebar v-model="currentView" />
      <main class="flex-1 p-8 overflow-auto">
        <DashboardView  v-if="currentView === 'dashboard'" />
        <BuildingsView  v-else-if="currentView === 'buildings'" />
        <UnitsView      v-else-if="currentView === 'units'" />
        <SensorsView    v-else-if="currentView === 'sensors'" />
        <ThresholdsView v-else-if="currentView === 'thresholds'" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import TheHeader     from './components/TheHeader.vue';
import AppSidebar    from './components/AppSidebar.vue';
import DashboardView  from './views/DashboardView.vue';
import BuildingsView  from './views/BuildingsView.vue';
import UnitsView      from './views/UnitsView.vue';
import SensorsView    from './views/SensorsView.vue';
import ThresholdsView from './views/ThresholdsView.vue';

const currentView = ref('dashboard');
</script>

<style>
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-emerald-600 text-white text-sm font-semibold rounded-xl
           hover:bg-emerald-700 transition-colors
           disabled:opacity-50 disabled:cursor-not-allowed;
  }
  .btn-secondary {
    @apply px-4 py-2 bg-slate-100 text-slate-700 text-sm font-semibold rounded-xl
           hover:bg-slate-200 transition-colors;
  }
  .btn-danger {
    @apply px-4 py-2 bg-red-500 text-white text-sm font-semibold rounded-xl
           hover:bg-red-600 transition-colors
           disabled:opacity-50 disabled:cursor-not-allowed;
  }
  .icon-btn {
    @apply p-1.5 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer;
  }
  .form-label {
    @apply block text-sm font-medium text-slate-700 mb-1;
  }
  .form-input {
    @apply w-full px-3 py-2 border border-slate-200 rounded-xl text-sm text-slate-800
           outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400
           transition-colors bg-white;
  }
}
</style>
