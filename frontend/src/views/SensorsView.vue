<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-slate-800">Sensors</h2>
      <button @click="openCreate" class="btn-primary flex items-center gap-2">
        <Plus :size="16" /> New Sensor
      </button>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 p-4 mb-6 flex gap-3 items-center shadow-sm">
      <Search :size="16" class="text-slate-400 shrink-0" />
      <input
        v-model="lookupId"
        placeholder="Lookup sensor by UUID…"
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
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Serial #</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Model</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Type</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Calibration</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Attached To</th>
            <th class="px-6 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="s in items"
            :key="s.sensor_id"
            class="border-b border-slate-50 hover:bg-slate-50 transition-colors"
          >
            <td class="px-6 py-4 font-mono text-xs font-medium text-slate-700">{{ s.serial_number }}</td>
            <td class="px-6 py-4 text-slate-600">{{ s.model }}</td>
            <td class="px-6 py-4">
              <span :class="[
                'px-2 py-0.5 rounded-full text-xs font-bold uppercase',
                s.sensor_type === 'COMMON' ? 'bg-violet-50 text-violet-700' : 'bg-teal-50 text-teal-700'
              ]">{{ s.sensor_type }}</span>
            </td>
            <td class="px-6 py-4 text-slate-500 text-xs">{{ s.calibration_date }}</td>
            <td class="px-6 py-4 font-mono text-xs text-slate-400">
              <span v-if="s.building_id" :title="s.building_id">Bldg {{ s.building_id.slice(0, 8) }}…</span>
              <span v-else-if="s.unit_id" :title="s.unit_id">Unit {{ s.unit_id.slice(0, 8) }}…</span>
              <span v-else class="text-slate-300">—</span>
            </td>
            <td class="px-6 py-4">
              <button @click="confirmDelete(s)" class="icon-btn text-slate-400 hover:text-red-500">
                <Trash2 :size="15" />
              </button>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="6" class="px-6 py-12 text-center text-slate-400">No sensors yet. Create one above.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <Modal v-model="showCreate" title="New Sensor">
      <form @submit.prevent="submitCreate" class="space-y-4">
        <div>
          <label class="form-label">Serial Number</label>
          <input v-model="form.serial_number" required class="form-input" placeholder="SN-001234" />
        </div>
        <div>
          <label class="form-label">Model</label>
          <input v-model="form.model" required class="form-input" placeholder="EnergiSense 3000" />
        </div>
        <div>
          <label class="form-label">Calibration Date</label>
          <input v-model="form.calibration_date" type="date" required class="form-input" />
        </div>
        <div>
          <label class="form-label">Sensor Type</label>
          <select v-model="form.sensor_type" class="form-input">
            <option value="COMMON">Common (building-level)</option>
            <option value="INDIVIDUAL">Individual (unit-level)</option>
          </select>
        </div>
        <div>
          <label class="form-label">Attach To</label>
          <div class="flex gap-4 mb-2">
            <label v-for="opt in attachOpts" :key="opt.value" class="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
              <input type="radio" v-model="attachTo" :value="opt.value" class="accent-emerald-600" />
              {{ opt.label }}
            </label>
          </div>
          <select v-if="attachTo === 'building'" v-model="form.building_id" class="form-input">
            <option value="">Select building…</option>
            <option v-for="b in buildings" :key="b.building_id" :value="b.building_id">
              {{ b.address }}
            </option>
          </select>
          <select v-else-if="attachTo === 'unit'" v-model="form.unit_id" class="form-input">
            <option value="">Select unit…</option>
            <option v-for="u in units" :key="u.unit_id" :value="u.unit_id">
              {{ u.unit_number }} — {{ u.owner_name }}
            </option>
          </select>
        </div>
        <div v-if="formError" class="text-sm text-red-600">{{ formError }}</div>
        <div class="flex gap-3 justify-end pt-2">
          <button type="button" @click="showCreate = false" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="loading" class="btn-primary">{{ loading ? 'Creating…' : 'Create' }}</button>
        </div>
      </form>
    </Modal>

    <Modal v-model="showDelete" title="Delete Sensor">
      <p class="text-sm text-slate-600 mb-6">
        Delete sensor <strong>{{ deleteTarget?.serial_number }}</strong>? This cannot be undone.
      </p>
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
import { sensorsApi } from '../api/index.js';
import { useLocalStore } from '../composables/useLocalStore.js';

const { items, upsert, remove } = useLocalStore('greenops_sensors', 'sensor_id');
const { items: buildings } = useLocalStore('greenops_buildings', 'building_id');
const { items: units } = useLocalStore('greenops_units', 'unit_id');

const lookupId = ref('');
const error = ref('');
const formError = ref('');
const loading = ref(false);
const showCreate = ref(false);
const showDelete = ref(false);
const deleteTarget = ref(null);
const attachTo = ref('none');

const attachOpts = [
  { value: 'building', label: 'Building' },
  { value: 'unit', label: 'Unit' },
  { value: 'none', label: 'None' },
];

const form = ref({
  serial_number: '',
  model: '',
  calibration_date: '',
  sensor_type: 'COMMON',
  building_id: null,
  unit_id: null,
});

const lookup = async () => {
  if (!lookupId.value.trim()) return;
  error.value = '';
  try {
    const { data } = await sensorsApi.get(lookupId.value.trim());
    upsert(data);
    lookupId.value = '';
  } catch (e) {
    error.value = e.response?.data?.detail || 'Sensor not found.';
  }
};

const openCreate = () => {
  form.value = { serial_number: '', model: '', calibration_date: '', sensor_type: 'COMMON', building_id: null, unit_id: null };
  attachTo.value = 'none';
  formError.value = '';
  showCreate.value = true;
};

const submitCreate = async () => {
  loading.value = true;
  formError.value = '';
  const payload = {
    serial_number: form.value.serial_number,
    model: form.value.model,
    calibration_date: form.value.calibration_date,
    sensor_type: form.value.sensor_type,
    building_id: attachTo.value === 'building' ? form.value.building_id || null : null,
    unit_id: attachTo.value === 'unit' ? form.value.unit_id || null : null,
  };
  try {
    const { data } = await sensorsApi.create(payload);
    upsert(data);
    showCreate.value = false;
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to create sensor.';
  } finally {
    loading.value = false;
  }
};

const confirmDelete = (s) => {
  deleteTarget.value = s;
  showDelete.value = true;
};

const submitDelete = async () => {
  loading.value = true;
  try {
    await sensorsApi.remove(deleteTarget.value.sensor_id);
    remove(deleteTarget.value.sensor_id);
    showDelete.value = false;
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to delete sensor.';
    showDelete.value = false;
  } finally {
    loading.value = false;
  }
};
</script>
