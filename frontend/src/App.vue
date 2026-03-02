<template>
  <div class="min-h-screen bg-slate-50 pb-12">
    <TheHeader />

    <main class="max-w-6xl mx-auto px-6 py-8">
      <BuildingTabs v-model="selectedBuilding" />
      
      <StatsCards 
        :value="currentData?.value" 
        :peak="peakValue" 
      />

      <UsageChart :history="historyData" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';
import axios from 'axios';

import TheHeader from './components/TheHeader.vue';
import BuildingTabs from './components/BuildingTabs.vue';
import StatsCards from './components/StatsCards.vue';
import UsageChart from './components/UsageChart.vue';

const selectedBuilding = ref(1);
const currentData = ref(null);
const historyData = ref([]);
const peakValue = ref(0);
let pollInterval = null;

const API_URL = "/api/v1/analytics";

const updateData = async () => {
  try {
    const [curr, hist] = await Promise.all([
      axios.get(`${API_URL}/${selectedBuilding.value}/current`),
      axios.get(`${API_URL}/${selectedBuilding.value}/history`)
    ]);

    currentData.value = curr.data;
    historyData.value = hist.data.reverse();

    if (curr.data.value > peakValue.value) {
      peakValue.value = curr.data.value;
    }
  } catch (e) {
    console.error("Poll error", e);
  }
};

onMounted(() => {
  updateData();
  pollInterval = setInterval(updateData, 3000);
});

onUnmounted(() => clearInterval(pollInterval));

watch(selectedBuilding, () => {
  peakValue.value = 0;
  currentData.value = null;
  historyData.value = [];
  updateData();
});
</script>

<style>
@tailwind base;
@tailwind components;
@tailwind utilities;
</style>