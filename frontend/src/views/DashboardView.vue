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

    <StatsCards :value="latestLoss" :peak="peakLoss" />
    <UsageChart :history="chartHistory" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { buildingsApi, energyBalancesApi } from '../api/index.js';
import { useLocalStore } from '../composables/useLocalStore.js';
import StatsCards from '../components/StatsCards.vue';
import UsageChart from '../components/UsageChart.vue';

const { items: buildings, setAll: setBuildings } = useLocalStore('greenops_buildings', 'building_id');

onMounted(async () => {
  if (!buildings.value.length) {
    try {
      const { data } = await buildingsApi.list({ page_size: 100 });
      setBuildings(data.items);
    } catch {}
  }
});

const selectedBuilding = ref(null);
const balances = ref([]);

const latestLoss = computed(() => balances.value[balances.value.length - 1]?.loss_kwh ?? 0);
const peakLoss = computed(() => Math.max(0, ...balances.value.map(b => b.loss_kwh)));
const chartHistory = computed(() =>
  balances.value.map(b => ({ timestamp: b.period_start, value: b.loss_kwh }))
);

const selectBuilding = (id) => {
  selectedBuilding.value = id;
};

const loadBalances = async () => {
  if (!selectedBuilding.value) return;
  const dateTo = new Date().toISOString();
  const dateFrom = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
  try {
    const { data } = await energyBalancesApi.list({
      building_id: selectedBuilding.value,
      date_from: dateFrom,
      date_to: dateTo,
    });
    balances.value = data;
  } catch {
    balances.value = [];
  }
};

// Auto-select first building — runs immediately and whenever buildings change (e.g. after Buildings view loads them)
watch(buildings, (list) => {
  if (!selectedBuilding.value && list.length) {
    selectedBuilding.value = list[0].building_id;
  }
}, { immediate: true });

watch(selectedBuilding, (id) => {
  balances.value = [];
  if (id) loadBalances();
}, { immediate: true });
</script>
