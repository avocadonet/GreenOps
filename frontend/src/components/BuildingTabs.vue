<template>
  <div class="flex items-center gap-4 mb-8">
    <div class="flex gap-2 p-1 bg-white rounded-xl border border-slate-200 w-fit shadow-sm">
      <button 
        v-for="id in [1, 2, 3]" :key="id"
        @click="$emit('update:modelValue', id)"
        :class="[
          'px-6 py-2 rounded-lg text-sm font-semibold transition-all',
          modelValue === id ? 'bg-slate-900 text-white shadow-md' : 'text-slate-500 hover:bg-slate-50'
        ]"
      >
        Building {{ id }}
      </button>
    </div>

    <button 
      @click="clearHistory"
      class="p-2 text-red-500 hover:bg-red-50 rounded-lg border border-red-100 transition-colors"
      title="Очистить историю"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
      </svg>
    </button>
  </div>
</template>

<script setup>
import axios from 'axios';

const props = defineProps(['modelValue']);
const emit = defineEmits(['update:modelValue']);

const clearHistory = async () => {
  const buildingId = props.modelValue;
  if (confirm(`Удалить всю историю потребления для Building ${buildingId}?`)) {
    try {
      await axios.delete(`/api/v1/analytics/${buildingId}/history`);
      alert("История успешно удалена из базы данных.");
      window.location.reload();
    } catch (e) {
      console.error("Delete error:", e);
      alert("Ошибка при удалении данных. Проверьте логи аналитики.");
    }
  }
};
</script>