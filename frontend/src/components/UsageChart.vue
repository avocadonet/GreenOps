<template>
  <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
    <div class="flex justify-between items-center mb-6">
      <h3 class="font-bold text-lg text-slate-800 tracking-tight">Consumption History</h3>
      <span class="text-[10px] text-slate-400 uppercase font-bold tracking-[0.2em]">Live Telemetry</span>
    </div>
    <div class="h-[350px]">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import Chart from 'chart.js/auto';

const props = defineProps(['history']);
const canvas = ref(null);
let chart = null;

const initChart = () => {
  if (!canvas.value) return;
  chart = new Chart(canvas.value.getContext('2d'), {
    type: 'line',
    data: {
      labels: [],
      datasets: [{ 
        label: 'kWh', 
        data: [], 
        borderColor: '#10b981', 
        backgroundColor: 'rgba(16, 185, 129, 0.05)',
        fill: true,
        tension: 0.4,
        pointRadius: 2
      }]
    },
    options: { 
      responsive: true, 
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: '#f8fafc' } },
        x: { grid: { display: false } }
      }
    }
  });
};

watch(() => props.history, (newData) => {
  if (!chart) return;
  chart.data.labels = newData.map(h => new Date(h.timestamp).toLocaleTimeString());
  chart.data.datasets[0].data = newData.map(h => h.value);
  chart.update('none');
}, { deep: true });

onMounted(initChart);
</script>