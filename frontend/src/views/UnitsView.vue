<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-slate-800">Units</h2>
      <button @click="openCreate" class="btn-primary flex items-center gap-2">
        <Plus :size="16" /> New Unit
      </button>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 p-4 mb-6 flex gap-3 items-center shadow-sm">
      <Search :size="16" class="text-slate-400 shrink-0" />
      <input
        v-model="lookupId"
        placeholder="Lookup unit by UUID…"
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
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Unit #</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Floor</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Owner</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Building</th>
            <th class="px-6 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="u in items"
            :key="u.unit_id"
            class="border-b border-slate-50 hover:bg-slate-50 transition-colors"
          >
            <td class="px-6 py-4 font-medium text-slate-800">{{ u.unit_number }}</td>
            <td class="px-6 py-4 text-slate-600">{{ u.floor }}</td>
            <td class="px-6 py-4 text-slate-600">{{ u.owner_name }}</td>
            <td class="px-6 py-4 font-mono text-xs text-slate-400" :title="u.building_id">
              {{ u.building_id.slice(0, 8) }}…
            </td>
            <td class="px-6 py-4">
              <div class="flex gap-1 justify-end">
                <button @click="openEdit(u)" class="icon-btn text-slate-400 hover:text-emerald-600">
                  <Pencil :size="15" />
                </button>
                <button @click="confirmDelete(u)" class="icon-btn text-slate-400 hover:text-red-500">
                  <Trash2 :size="15" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="5" class="px-6 py-12 text-center text-slate-400">No units yet. Create one above.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <Modal v-model="showCreate" title="New Unit">
      <form @submit.prevent="submitCreate" class="space-y-4">
        <div>
          <label class="form-label">Building</label>
          <select v-model="form.building_id" required class="form-input">
            <option value="">Select a building…</option>
            <option v-for="b in buildings" :key="b.building_id" :value="b.building_id">
              {{ b.address }}
            </option>
          </select>
          <p v-if="!buildings.length" class="text-xs text-amber-600 mt-1">
            No buildings found — create buildings first.
          </p>
        </div>
        <div>
          <label class="form-label">Unit Number</label>
          <input v-model="form.unit_number" required class="form-input" placeholder="A-101" />
        </div>
        <div>
          <label class="form-label">Floor</label>
          <input v-model.number="form.floor" type="number" required class="form-input" placeholder="1" />
        </div>
        <div>
          <label class="form-label">Owner Name</label>
          <input v-model="form.owner_name" required class="form-input" placeholder="John Doe" />
        </div>
        <div v-if="formError" class="text-sm text-red-600">{{ formError }}</div>
        <div class="flex gap-3 justify-end pt-2">
          <button type="button" @click="showCreate = false" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="loading" class="btn-primary">{{ loading ? 'Creating…' : 'Create' }}</button>
        </div>
      </form>
    </Modal>

    <Modal v-model="showEdit" title="Edit Unit">
      <form @submit.prevent="submitEdit" class="space-y-4">
        <div>
          <label class="form-label">Unit Number</label>
          <input v-model="editForm.unit_number" required class="form-input" />
        </div>
        <div>
          <label class="form-label">Floor</label>
          <input v-model.number="editForm.floor" type="number" required class="form-input" />
        </div>
        <div>
          <label class="form-label">Owner Name</label>
          <input v-model="editForm.owner_name" required class="form-input" />
        </div>
        <div v-if="formError" class="text-sm text-red-600">{{ formError }}</div>
        <div class="flex gap-3 justify-end pt-2">
          <button type="button" @click="showEdit = false" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="loading" class="btn-primary">{{ loading ? 'Saving…' : 'Save' }}</button>
        </div>
      </form>
    </Modal>

    <Modal v-model="showDelete" title="Delete Unit">
      <p class="text-sm text-slate-600 mb-6">
        Delete unit <strong>{{ deleteTarget?.unit_number }}</strong>? This cannot be undone.
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
import { unitsApi } from '../api/index.js';
import { useLocalStore } from '../composables/useLocalStore.js';

const { items, upsert, remove } = useLocalStore('greenops_units', 'unit_id');
const { items: buildings } = useLocalStore('greenops_buildings', 'building_id');

const lookupId = ref('');
const error = ref('');
const formError = ref('');
const loading = ref(false);
const showCreate = ref(false);
const showEdit = ref(false);
const showDelete = ref(false);
const deleteTarget = ref(null);
const editTarget = ref(null);

const form = ref({ building_id: '', unit_number: '', floor: '', owner_name: '' });
const editForm = ref({ unit_number: '', floor: '', owner_name: '' });

const lookup = async () => {
  if (!lookupId.value.trim()) return;
  error.value = '';
  try {
    const { data } = await unitsApi.get(lookupId.value.trim());
    upsert(data);
    lookupId.value = '';
  } catch (e) {
    error.value = e.response?.data?.detail || 'Unit not found.';
  }
};

const openCreate = () => {
  form.value = { building_id: '', unit_number: '', floor: '', owner_name: '' };
  formError.value = '';
  showCreate.value = true;
};

const submitCreate = async () => {
  loading.value = true;
  formError.value = '';
  try {
    const { data } = await unitsApi.create(form.value);
    upsert(data);
    showCreate.value = false;
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to create unit.';
  } finally {
    loading.value = false;
  }
};

const openEdit = (u) => {
  editTarget.value = u;
  editForm.value = { unit_number: u.unit_number, floor: u.floor, owner_name: u.owner_name };
  formError.value = '';
  showEdit.value = true;
};

const submitEdit = async () => {
  loading.value = true;
  formError.value = '';
  try {
    const { data } = await unitsApi.update(editTarget.value.unit_id, editForm.value);
    upsert(data);
    showEdit.value = false;
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to update unit.';
  } finally {
    loading.value = false;
  }
};

const confirmDelete = (u) => {
  deleteTarget.value = u;
  showDelete.value = true;
};

const submitDelete = async () => {
  loading.value = true;
  try {
    await unitsApi.remove(deleteTarget.value.unit_id);
    remove(deleteTarget.value.unit_id);
    showDelete.value = false;
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to delete unit.';
    showDelete.value = false;
  } finally {
    loading.value = false;
  }
};
</script>
