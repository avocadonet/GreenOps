<template>
  <div class="flex gap-2 p-1 bg-white rounded-xl border border-slate-200 w-fit shadow-sm mb-8">
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
</template>

<script setup>
defineProps(['modelValue']);
defineEmits(['update:modelValue']);
</script>