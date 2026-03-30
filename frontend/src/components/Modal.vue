<template>
  <Teleport to="body">
    <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/40" @click="$emit('update:modelValue', false)" />
      <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
        <div class="flex justify-between items-center mb-5">
          <h3 class="text-lg font-bold text-slate-800">{{ title }}</h3>
          <button
            @click="$emit('update:modelValue', false)"
            class="text-slate-400 hover:text-slate-600 transition-colors p-1 rounded-lg hover:bg-slate-100"
          >
            <X :size="18" />
          </button>
        </div>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { X } from 'lucide-vue-next';
defineProps({ modelValue: Boolean, title: String });
defineEmits(['update:modelValue']);
</script>
