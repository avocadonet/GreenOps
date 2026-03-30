<template>
  <div>
    <h2 class="text-2xl font-bold text-slate-800 mb-6">Dashboard</h2>

    <div class="flex gap-2 p-1 bg-white rounded-xl border border-slate-200 w-fit shadow-sm mb-8 flex-wrap">
      <button
        v-for="b in buildings"
        :key="b.building_id"
        @click="selectBuilding(b.building_id)"
        :class="[
          'px-5 py-2 rounded-lg text-sm font-semibold transition-all',
          selectedBuilding === b.building_id
            ? 'bg-slate-900 text-white shadow-md'
            : 'text-slate-500 hover:bg-slate-50'
        ]"
      >
        {{ b.address }}
      </button>
      <span v-if="!buildings.length" class="px-5 py-2 text-sm text-slate-400 italic">
        No buildings — add them in the Buildings view
      </span>
    </div>

    <StatsCards :value="currentData?.value" :peak="peakValue" />
    <UsageChart :history="historyData" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { analyticsApi } from '../api/index.js';
import { useLocalStore } from '../composables/useLocalStore.js';
import StatsCards from '../components/StatsCards.vue';
import UsageChart from '../components/UsageChart.vue';

const { items: buildings } = useLocalStore('greenops_buildings', 'building_id');

const selectedBuilding = ref(buildings.value[0]?.building_id ?? null);
const currentData = ref(null);
const historyData = ref([]);
const peakValue = ref(0);
let pollInterval = null;

const selectBuilding = (id) => {
  selectedBuilding.value = id;
};

const updateData = async () => {
  if (!selectedBuilding.value) return;
  try {
    const [curr, hist] = await Promise.all([
      analyticsApi.current(selectedBuilding.value),
      analyticsApi.history(selectedBuilding.value),
    ]);
    currentData.value = curr.data;
    historyData.value = hist.data.reverse();
    if (curr.data.value > peakValue.value) peakValue.value = curr.data.value;
  } catch {
    // analytics service may not be running
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
