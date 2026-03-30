<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-slate-800">Thresholds</h2>
      <button @click="openCreate" class="btn-primary flex items-center gap-2">
        <Plus :size="16" /> New Threshold
      </button>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 p-4 mb-6 flex gap-3 items-center shadow-sm">
      <Search :size="16" class="text-slate-400 shrink-0" />
      <input
        v-model="lookupId"
        placeholder="Lookup threshold by UUID…"
        class="flex-1 text-sm outline-none text-slate-700 placeholder-slate-400"
        @keydown.enter="lookup"
      />
      <button @click="lookup" :disabled="!lookupId.trim()" class="btn-secondary text-xs">Fetch</button>
    </div>

    <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600">{{ error }}</div>

    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-slate-100 bg-slate-50">
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Sensor</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Limit (kWh)</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Type</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Tariff Zone</th>
            <th class="px-6 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="t in items"
            :key="t.threshold_id"
            class="border-b border-slate-50 hover:bg-slate-50 transition-colors"
          >
            <td class="px-6 py-4 font-mono text-xs text-slate-500" :title="t.sensor_id">
              {{ sensorLabel(t.sensor_id) }}
            </td>
            <td class="px-6 py-4 font-semibold text-slate-800">{{ t.limit_value }}</td>
            <td class="px-6 py-4">
              <span :class="[
                'px-2 py-0.5 rounded-full text-xs font-bold uppercase',
                t.threshold_type === 'UPPER' ? 'bg-red-50 text-red-700' : 'bg-blue-50 text-blue-700'
              ]">{{ t.threshold_type }}</span>
            </td>
            <td class="px-6 py-4">
              <span :class="[
                'px-2 py-0.5 rounded-full text-xs font-bold uppercase',
                t.tariff_zone === 'DAY' ? 'bg-amber-50 text-amber-700' : 'bg-indigo-50 text-indigo-700'
              ]">{{ t.tariff_zone }}</span>
            </td>
            <td class="px-6 py-4">
              <button @click="confirmDelete(t)" class="icon-btn text-slate-400 hover:text-red-500">
                <Trash2 :size="15" />
              </button>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="5" class="px-6 py-12 text-center text-slate-400">No thresholds yet. Create one above.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <Modal v-model="showCreate" title="New Threshold">
      <form @submit.prevent="submitCreate" class="space-y-4">
        <div>
          <label class="form-label">Sensor</label>
          <select v-model="form.sensor_id" required class="form-input">
            <option value="">Select a sensor…</option>
            <option v-for="s in sensors" :key="s.sensor_id" :value="s.sensor_id">
              {{ s.serial_number }} — {{ s.model }}
            </option>
          </select>
          <p v-if="!sensors.length" class="text-xs text-amber-600 mt-1">
            No sensors found — create sensors first.
          </p>
        </div>
        <div>
          <label class="form-label">Limit Value (kWh)</label>
          <input v-model.number="form.limit_value" type="number" step="0.01" min="0" required class="form-input" placeholder="100.00" />
        </div>
        <div>
          <label class="form-label">Threshold Type</label>
          <select v-model="form.threshold_type" class="form-input">
            <option value="UPPER">Upper</option>
            <option value="LOWER">Lower</option>
          </select>
        </div>
        <div>
          <label class="form-label">Tariff Zone</label>
          <select v-model="form.tariff_zone" class="form-input">
            <option value="DAY">Day</option>
            <option value="NIGHT">Night</option>
          </select>
        </div>
        <div v-if="formError" class="text-sm text-red-600">{{ formError }}</div>
        <div class="flex gap-3 justify-end pt-2">
          <button type="button" @click="showCreate = false" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="loading" class="btn-primary">{{ loading ? 'Creating…' : 'Create' }}</button>
        </div>
      </form>
    </Modal>

    <Modal v-model="showDelete" title="Delete Threshold">
      <p class="text-sm text-slate-600 mb-6">Delete this threshold? This cannot be undone.</p>
      <div class="flex gap-3 justify-end">
        <button @click="showDelete = false" class="btn-secondary">Cancel</button>
        <button @click="submitDelete" :disabled="loading" class="btn-danger">{{ loading ? 'Deleting…' : 'Delete' }}</button>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Plus, Search, Trash2 } from 'lucide-vue-next';
import Modal from '../components/Modal.vue';
import { thresholdsApi } from '../api/index.js';
import { useLocalStore } from '../composables/useLocalStore.js';

const { items, upsert, remove } = useLocalStore('greenops_thresholds', 'threshold_id');
const { items: sensors } = useLocalStore('greenops_sensors', 'sensor_id');

const lookupId = ref('');
const error = ref('');
const formError = ref('');
const loading = ref(false);
const showCreate = ref(false);
const showDelete = ref(false);
const deleteTarget = ref(null);

const form = ref({ sensor_id: '', limit_value: '', threshold_type: 'UPPER', tariff_zone: 'DAY' });

const sensorLabel = (id) => {
  const s = sensors.value.find(s => s.sensor_id === id);
  return s ? `${s.serial_number}` : `${id.slice(0, 8)}…`;
};

const lookup = async () => {
  if (!lookupId.value.trim()) return;
  error.value = '';
  try {
    const { data } = await thresholdsApi.get(lookupId.value.trim());
    upsert(data);
    lookupId.value = '';
  } catch (e) {
    error.value = e.response?.data?.detail || 'Threshold not found.';
  }
};

const openCreate = () => {
  form.value = { sensor_id: '', limit_value: '', threshold_type: 'UPPER', tariff_zone: 'DAY' };
  formError.value = '';
  showCreate.value = true;
};

const submitCreate = async () => {
  loading.value = true;
  formError.value = '';
  try {
    const { data } = await thresholdsApi.create(form.value);
    upsert(data);
    showCreate.value = false;
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to create threshold.';
  } finally {
    loading.value = false;
  }
};

const confirmDelete = (t) => {
  deleteTarget.value = t;
  showDelete.value = true;
};

const submitDelete = async () => {
  loading.value = true;
  try {
    await thresholdsApi.remove(deleteTarget.value.threshold_id);
    remove(deleteTarget.value.threshold_id);
    showDelete.value = false;
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to delete threshold.';
    showDelete.value = false;
  } finally {
    loading.value = false;
  }
};
</script>
