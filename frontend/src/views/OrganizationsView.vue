<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-slate-800">Organizations</h2>
      <button @click="openCreate" class="btn-primary flex items-center gap-2">
        <Plus :size="16" /> New Organization
      </button>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 p-4 mb-6 flex gap-3 items-center shadow-sm">
      <Search :size="16" class="text-slate-400 shrink-0" />
      <input
        v-model="lookupId"
        placeholder="Lookup organization by ID…"
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
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Name</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Contact Email</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Created</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">ID</th>
            <th class="px-6 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="org in items"
            :key="org.id"
            class="border-b border-slate-50 hover:bg-slate-50 transition-colors"
          >
            <td class="px-6 py-4 font-medium text-slate-800">{{ org.name }}</td>
            <td class="px-6 py-4 text-slate-500 text-xs">{{ org.contact_email || '—' }}</td>
            <td class="px-6 py-4 text-slate-400 text-xs">
              {{ org.created_at ? new Date(org.created_at).toLocaleDateString() : '—' }}
            </td>
            <td class="px-6 py-4 font-mono text-xs text-slate-400">{{ org.id }}</td>
            <td class="px-6 py-4">
              <div class="flex gap-1 justify-end">
                <button @click="openEdit(org)" class="icon-btn text-slate-400 hover:text-emerald-600">
                  <Pencil :size="15" />
                </button>
                <button @click="confirmDelete(org)" class="icon-btn text-slate-400 hover:text-red-500">
                  <Trash2 :size="15" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="5" class="px-6 py-12 text-center text-slate-400">No organizations yet. Create one above.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <Modal v-model="showCreate" title="New Organization">
      <form @submit.prevent="submitCreate" class="space-y-4">
        <div>
          <label class="form-label">Name</label>
          <input v-model="form.name" required class="form-input" placeholder="Acme Corp" />
        </div>
        <div>
          <label class="form-label">Description</label>
          <input v-model="form.description" class="form-input" placeholder="Optional" />
        </div>
        <div>
          <label class="form-label">Contact Email</label>
          <input v-model="form.contact_email" type="email" class="form-input" placeholder="ops@example.com" />
        </div>
        <div v-if="formError" class="text-sm text-red-600">{{ formError }}</div>
        <div class="flex gap-3 justify-end pt-2">
          <button type="button" @click="showCreate = false" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="loading" class="btn-primary">{{ loading ? 'Creating…' : 'Create' }}</button>
        </div>
      </form>
    </Modal>

    <Modal v-model="showEdit" title="Edit Organization">
      <form @submit.prevent="submitEdit" class="space-y-4">
        <div>
          <label class="form-label">Name</label>
          <input v-model="editForm.name" required class="form-input" />
        </div>
        <div>
          <label class="form-label">Description</label>
          <input v-model="editForm.description" class="form-input" />
        </div>
        <div>
          <label class="form-label">Contact Email</label>
          <input v-model="editForm.contact_email" type="email" class="form-input" />
        </div>
        <div v-if="formError" class="text-sm text-red-600">{{ formError }}</div>
        <div class="flex gap-3 justify-end pt-2">
          <button type="button" @click="showEdit = false" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="loading" class="btn-primary">{{ loading ? 'Saving…' : 'Save' }}</button>
        </div>
      </form>
    </Modal>

    <Modal v-model="showDelete" title="Delete Organization">
      <p class="text-sm text-slate-600 mb-6">
        Delete <strong>{{ deleteTarget?.name }}</strong>? This cannot be undone.
      </p>
      <div class="flex gap-3 justify-end">
        <button @click="showDelete = false" class="btn-secondary">Cancel</button>
        <button @click="submitDelete" :disabled="loading" class="btn-danger">{{ loading ? 'Deleting…' : 'Delete' }}</button>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Plus, Search, Pencil, Trash2 } from 'lucide-vue-next';
import Modal from '../components/Modal.vue';
import { organizationsApi } from '../api/index.js';
import { useLocalStore } from '../composables/useLocalStore.js';

const { items, setAll, upsert, remove } = useLocalStore('greenops_organizations', 'id');

onMounted(async () => {
  try {
    const { data } = await organizationsApi.list({ page_size: 100 });
    setAll(data.items);
  } catch {}
});

const lookupId = ref('');
const error = ref('');
const formError = ref('');
const loading = ref(false);
const showCreate = ref(false);
const showEdit = ref(false);
const showDelete = ref(false);
const deleteTarget = ref(null);
const editTarget = ref(null);

const form = ref({ name: '', description: '', contact_email: '' });
const editForm = ref({ name: '', description: '', contact_email: '' });

const lookup = async () => {
  if (!lookupId.value.trim()) return;
  error.value = '';
  try {
    const { data } = await organizationsApi.get(lookupId.value.trim());
    upsert(data);
    lookupId.value = '';
  } catch (e) {
    error.value = e.response?.data?.detail || 'Organization not found.';
  }
};

const openCreate = () => {
  form.value = { name: '', description: '', contact_email: '' };
  formError.value = '';
  showCreate.value = true;
};

const submitCreate = async () => {
  loading.value = true;
  formError.value = '';
  try {
    const payload = {
      name: form.value.name,
      description: form.value.description || null,
      contact_email: form.value.contact_email || null,
    };
    const { data } = await organizationsApi.create(payload);
    upsert(data);
    showCreate.value = false;
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to create organization.';
  } finally {
    loading.value = false;
  }
};

const openEdit = (org) => {
  editTarget.value = org;
  editForm.value = { name: org.name, description: org.description || '', contact_email: org.contact_email || '' };
  formError.value = '';
  showEdit.value = true;
};

const submitEdit = async () => {
  loading.value = true;
  formError.value = '';
  try {
    const payload = {
      name: editForm.value.name,
      description: editForm.value.description || null,
      contact_email: editForm.value.contact_email || null,
    };
    const { data } = await organizationsApi.update(editTarget.value.id, payload);
    upsert(data);
    showEdit.value = false;
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to update organization.';
  } finally {
    loading.value = false;
  }
};

const confirmDelete = (org) => {
  deleteTarget.value = org;
  showDelete.value = true;
};

const submitDelete = async () => {
  loading.value = true;
  try {
    await organizationsApi.remove(deleteTarget.value.id);
    remove(deleteTarget.value.id);
    showDelete.value = false;
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to delete organization.';
    showDelete.value = false;
  } finally {
    loading.value = false;
  }
};
</script>
