<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-slate-800">Buildings</h2>
      <button @click="openCreate" class="btn-primary flex items-center gap-2">
        <Plus :size="16" /> New Building
      </button>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 p-4 mb-6 flex gap-3 items-center shadow-sm">
      <Search :size="16" class="text-slate-400 shrink-0" />
      <input
        v-model="lookupId"
        placeholder="Lookup building by UUID…"
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
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Address</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Type</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Area (m²)</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">ID</th>
            <th class="px-6 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="b in items"
            :key="b.building_id"
            class="border-b border-slate-50 hover:bg-slate-50 transition-colors"
          >
            <td class="px-6 py-4 font-medium text-slate-800">{{ b.address }}</td>
            <td class="px-6 py-4">
              <span :class="[
                'px-2 py-0.5 rounded-full text-xs font-bold uppercase',
                b.building_type === 'RESIDENTIAL' ? 'bg-sky-50 text-sky-700' : 'bg-amber-50 text-amber-700'
              ]">{{ b.building_type }}</span>
            </td>
            <td class="px-6 py-4 text-slate-600">{{ b.total_area }}</td>
            <td class="px-6 py-4 font-mono text-xs text-slate-400" :title="b.building_id">
              {{ b.building_id.slice(0, 8) }}…
            </td>
            <td class="px-6 py-4">
              <div class="flex gap-1 justify-end">
                <button @click="openEdit(b)" class="icon-btn text-slate-400 hover:text-emerald-600">
                  <Pencil :size="15" />
                </button>
                <button @click="confirmDelete(b)" class="icon-btn text-slate-400 hover:text-red-500">
                  <Trash2 :size="15" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="5" class="px-6 py-12 text-center text-slate-400">No buildings yet. Create one above.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <Modal v-model="showCreate" title="New Building">
      <form @submit.prevent="submitCreate" class="space-y-4">
        <div>
          <label class="form-label">Address</label>
          <input v-model="form.address" required class="form-input" placeholder="123 Main St" />
        </div>
        <div>
          <label class="form-label">Building Type</label>
          <select v-model="form.building_type" class="form-input">
            <option value="RESIDENTIAL">Residential</option>
            <option value="INDUSTRIAL">Industrial</option>
          </select>
        </div>
        <div>
          <label class="form-label">Total Area (m²)</label>
          <input v-model.number="form.total_area" type="number" step="0.01" min="0" required class="form-input" placeholder="1500.00" />
        </div>
        <div v-if="formError" class="text-sm text-red-600">{{ formError }}</div>
        <div class="flex gap-3 justify-end pt-2">
          <button type="button" @click="showCreate = false" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="loading" class="btn-primary">{{ loading ? 'Creating…' : 'Create' }}</button>
        </div>
      </form>
    </Modal>

    <Modal v-model="showEdit" title="Edit Building">
      <form @submit.prevent="submitEdit" class="space-y-4">
        <div>
          <label class="form-label">Address</label>
          <input v-model="editForm.address" required class="form-input" />
        </div>
        <div>
          <label class="form-label">Total Area (m²)</label>
          <input v-model.number="editForm.total_area" type="number" step="0.01" min="0" required class="form-input" />
        </div>
        <div v-if="formError" class="text-sm text-red-600">{{ formError }}</div>
        <div class="flex gap-3 justify-end pt-2">
          <button type="button" @click="showEdit = false" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="loading" class="btn-primary">{{ loading ? 'Saving…' : 'Save' }}</button>
        </div>
      </form>
    </Modal>

    <Modal v-model="showDelete" title="Delete Building">
      <p class="text-sm text-slate-600 mb-6">
        Delete <strong>{{ deleteTarget?.address }}</strong>? This cannot be undone.
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
import { Plus, Search, Pencil, Trash2 } from 'lucide-vue-next';
import Modal from '../components/Modal.vue';
import { buildingsApi } from '../api/index.js';
import { useLocalStore } from '../composables/useLocalStore.js';

const { items, upsert, remove } = useLocalStore('greenops_buildings', 'building_id');

const lookupId = ref('');
const error = ref('');
const formError = ref('');
const loading = ref(false);
const showCreate = ref(false);
const showEdit = ref(false);
const showDelete = ref(false);
const deleteTarget = ref(null);
const editTarget = ref(null);

const form = ref({ address: '', building_type: 'RESIDENTIAL', total_area: '' });
const editForm = ref({ address: '', total_area: '' });

const lookup = async () => {
  if (!lookupId.value.trim()) return;
  error.value = '';
  try {
    const { data } = await buildingsApi.get(lookupId.value.trim());
    upsert(data);
    lookupId.value = '';
  } catch (e) {
    error.value = e.response?.data?.detail || 'Building not found.';
  }
};

const openCreate = () => {
  form.value = { address: '', building_type: 'RESIDENTIAL', total_area: '' };
  formError.value = '';
  showCreate.value = true;
};

const submitCreate = async () => {
  loading.value = true;
  formError.value = '';
  try {
    const { data } = await buildingsApi.create(form.value);
    upsert(data);
    showCreate.value = false;
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to create building.';
  } finally {
    loading.value = false;
  }
};

const openEdit = (b) => {
  editTarget.value = b;
  editForm.value = { address: b.address, total_area: b.total_area };
  formError.value = '';
  showEdit.value = true;
};

const submitEdit = async () => {
  loading.value = true;
  formError.value = '';
  try {
    const { data } = await buildingsApi.update(editTarget.value.building_id, editForm.value);
    upsert(data);
    showEdit.value = false;
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to update building.';
  } finally {
    loading.value = false;
  }
};

const confirmDelete = (b) => {
  deleteTarget.value = b;
  showDelete.value = true;
};

const submitDelete = async () => {
  loading.value = true;
  try {
    await buildingsApi.remove(deleteTarget.value.building_id);
    remove(deleteTarget.value.building_id);
    showDelete.value = false;
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to delete building.';
    showDelete.value = false;
  } finally {
    loading.value = false;
  }
};
</script>
