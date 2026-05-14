<template>
  <div>
    <h2 class="text-2xl font-bold text-slate-800 mb-6">Users</h2>

    <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600">{{ error }}</div>

    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-slate-100 bg-slate-50">
            <th class="text-left px-6 py-3 font-semibold text-slate-500">ID</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Email</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Name</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Role</th>
            <th class="text-left px-6 py-3 font-semibold text-slate-500">Status</th>
            <th class="px-6 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="u in users"
            :key="u.id"
            class="border-b border-slate-50 hover:bg-slate-50 transition-colors"
          >
            <td class="px-6 py-4 font-mono text-xs text-slate-400">{{ u.id }}</td>
            <td class="px-6 py-4 text-slate-700">{{ u.email }}</td>
            <td class="px-6 py-4 text-slate-600">{{ u.fullname || '—' }}</td>
            <td class="px-6 py-4">
              <span class="px-2 py-0.5 rounded-lg text-xs font-semibold" :class="roleBadge(u.role)">
                {{ u.role }}
              </span>
            </td>
            <td class="px-6 py-4">
              <span :class="u.is_active ? 'text-emerald-600' : 'text-slate-400'" class="text-xs font-medium">
                {{ u.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-6 py-4">
              <button @click="openRoles(u)" class="btn-secondary text-xs">Manage Roles</button>
            </td>
          </tr>
          <tr v-if="!users.length">
            <td colspan="6" class="px-6 py-12 text-center text-slate-400">No users found.</td>
          </tr>
        </tbody>
      </table>

      <div class="flex items-center justify-between px-6 py-3 border-t border-slate-100 bg-slate-50">
        <span class="text-xs text-slate-400">Page {{ page }}</span>
        <div class="flex gap-2">
          <button :disabled="page === 1" @click="changePage(page - 1)" class="btn-secondary text-xs">Prev</button>
          <button :disabled="users.length < pageSize" @click="changePage(page + 1)" class="btn-secondary text-xs">Next</button>
        </div>
      </div>
    </div>

    <!-- Roles modal -->
    <Modal v-model="showRoles" :title="`Roles — ${rolesTarget?.email}`">
      <div v-if="rolesError" class="mb-3 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600">{{ rolesError }}</div>

      <div class="mb-4">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-100">
              <th class="text-left py-2 font-semibold text-slate-500">Org ID</th>
              <th class="text-left py-2 font-semibold text-slate-500">Role</th>
              <th class="py-2"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in targetRoles" :key="r.organization_id" class="border-b border-slate-50">
              <td class="py-2 font-mono text-xs text-slate-400">{{ r.organization_id }}</td>
              <td class="py-2">
                <span class="px-2 py-0.5 rounded-lg text-xs font-semibold" :class="roleBadge(r.role)">{{ r.role }}</span>
              </td>
              <td class="py-2">
                <div class="flex gap-1 justify-end">
                  <button @click="openEditRole(r)" :disabled="!canManage(r.role)" class="icon-btn text-slate-400 hover:text-emerald-600 disabled:opacity-30 disabled:cursor-not-allowed">
                    <Pencil :size="14" />
                  </button>
                  <button @click="confirmDeleteRole(r)" :disabled="!canManage(r.role)" class="icon-btn text-slate-400 hover:text-red-500 disabled:opacity-30 disabled:cursor-not-allowed">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!targetRoles.length">
              <td colspan="3" class="py-6 text-center text-slate-400 text-xs">No org roles assigned.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="assignableRoles.length" class="border-t border-slate-100 pt-4">
        <p class="text-xs font-semibold text-slate-500 mb-3">Assign New Role</p>
        <form @submit.prevent="submitCreateRole" class="space-y-3">
          <div>
            <label class="form-label">Organization ID</label>
            <input v-model.number="roleForm.organization_id" type="number" required class="form-input" placeholder="1" />
          </div>
          <div>
            <label class="form-label">Role</label>
            <select v-model="roleForm.role" required class="form-input">
              <option v-for="r in assignableRoles" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="flex gap-3 justify-end">
            <button type="submit" :disabled="rolesLoading" class="btn-primary text-xs">
              {{ rolesLoading ? 'Assigning…' : 'Assign' }}
            </button>
          </div>
        </form>
      </div>
    </Modal>

    <!-- Edit role modal -->
    <Modal v-model="showEditRole" title="Update Role">
      <form @submit.prevent="submitEditRole" class="space-y-4">
        <div>
          <label class="form-label">Role</label>
          <select v-model="editRoleForm.role" required class="form-input">
            <option v-for="r in assignableRoles" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
        <div v-if="rolesError" class="text-sm text-red-600">{{ rolesError }}</div>
        <div class="flex gap-3 justify-end pt-2">
          <button type="button" @click="showEditRole = false" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="rolesLoading" class="btn-primary">{{ rolesLoading ? 'Saving…' : 'Save' }}</button>
        </div>
      </form>
    </Modal>

    <!-- Delete role confirm -->
    <Modal v-model="showDeleteRole" title="Remove Role">
      <p class="text-sm text-slate-600 mb-6">
        Remove <strong>{{ deleteRoleTarget?.role }}</strong> role in org
        <strong>{{ deleteRoleTarget?.organization_id }}</strong>? This cannot be undone.
      </p>
      <div class="flex gap-3 justify-end">
        <button @click="showDeleteRole = false" class="btn-secondary">Cancel</button>
        <button @click="submitDeleteRole" :disabled="rolesLoading" class="btn-danger">
          {{ rolesLoading ? 'Removing…' : 'Remove' }}
        </button>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { Pencil, Trash2 } from 'lucide-vue-next';
import Modal from '../components/Modal.vue';
import { usersApi, userRolesApi } from '../api/index.js';

// Role hierarchy: index = priority (lower index = higher rank)
const ROLE_ORDER = [
  'SUPER_USER', 'SUPER_OWNER', 'SUPER_ADMIN', 'SUPER_REDACTOR',
  'ORGANIZATION_OWNER', 'OWNER', 'ADMIN', 'REDACTOR', 'PUBLIC',
];

const users = ref([]);
const error = ref('');
const page = ref(1);
const pageSize = 20;
const me = ref(null);

onMounted(async () => {
  try {
    const { data } = await usersApi.me();
    me.value = data;
  } catch {}
  await loadUsers();
});

const loadUsers = async () => {
  error.value = '';
  try {
    const { data } = await usersApi.list({ page: page.value, page_size: pageSize });
    users.value = data.items;
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load users.';
  }
};

const changePage = async (p) => {
  page.value = p;
  await loadUsers();
};

// Roles assignable by the current user (strictly lower rank)
const myRank = computed(() => {
  if (!me.value) return Infinity;
  const idx = ROLE_ORDER.indexOf(me.value.role);
  return idx === -1 ? Infinity : idx;
});

const assignableRoles = computed(() =>
  ROLE_ORDER.filter((r, i) => i > myRank.value && !r.startsWith('SUPER'))
);

const canManage = (role) => {
  const targetRank = ROLE_ORDER.indexOf(role);
  return myRank.value < targetRank;
};

// Roles modal state
const showRoles = ref(false);
const rolesTarget = ref(null);
const targetRoles = ref([]);
const rolesError = ref('');
const rolesLoading = ref(false);
const roleForm = ref({ organization_id: '', role: '' });

const loadRoles = async (userId) => {
  try {
    const { data } = await userRolesApi.list(userId);
    targetRoles.value = data;
  } catch (e) {
    rolesError.value = e.response?.data?.detail || 'Failed to load roles.';
  }
};

const openRoles = async (u) => {
  rolesTarget.value = u;
  rolesError.value = '';
  roleForm.value = { organization_id: '', role: assignableRoles.value[0] || '' };
  targetRoles.value = [];
  showRoles.value = true;
  await loadRoles(u.id);
};

const submitCreateRole = async () => {
  rolesLoading.value = true;
  rolesError.value = '';
  try {
    await userRolesApi.create(rolesTarget.value.id, {
      user_id: rolesTarget.value.id,
      organization_id: roleForm.value.organization_id,
      role: roleForm.value.role,
    });
    roleForm.value = { organization_id: '', role: assignableRoles.value[0] || '' };
    await loadRoles(rolesTarget.value.id);
  } catch (e) {
    rolesError.value = e.response?.data?.detail || 'Failed to assign role.';
  } finally {
    rolesLoading.value = false;
  }
};

// Edit role
const showEditRole = ref(false);
const editRoleTarget = ref(null);
const editRoleForm = ref({ role: '' });

const openEditRole = (r) => {
  editRoleTarget.value = r;
  editRoleForm.value = { role: r.role };
  rolesError.value = '';
  showEditRole.value = true;
};

const submitEditRole = async () => {
  rolesLoading.value = true;
  rolesError.value = '';
  try {
    await userRolesApi.update(
      rolesTarget.value.id,
      editRoleTarget.value.organization_id,
      { role: editRoleForm.value.role },
    );
    showEditRole.value = false;
    await loadRoles(rolesTarget.value.id);
  } catch (e) {
    rolesError.value = e.response?.data?.detail || 'Failed to update role.';
  } finally {
    rolesLoading.value = false;
  }
};

// Delete role
const showDeleteRole = ref(false);
const deleteRoleTarget = ref(null);

const confirmDeleteRole = (r) => {
  deleteRoleTarget.value = r;
  rolesError.value = '';
  showDeleteRole.value = true;
};

const submitDeleteRole = async () => {
  rolesLoading.value = true;
  try {
    await userRolesApi.remove(rolesTarget.value.id, deleteRoleTarget.value.organization_id);
    showDeleteRole.value = false;
    await loadRoles(rolesTarget.value.id);
  } catch (e) {
    rolesError.value = e.response?.data?.detail || 'Failed to remove role.';
    showDeleteRole.value = false;
  } finally {
    rolesLoading.value = false;
  }
};

// Visual helpers
const roleBadge = (role) => {
  const rank = ROLE_ORDER.indexOf(role);
  if (rank <= 1) return 'bg-purple-100 text-purple-700';
  if (rank <= 3) return 'bg-blue-100 text-blue-700';
  if (rank <= 5) return 'bg-emerald-100 text-emerald-700';
  return 'bg-slate-100 text-slate-600';
};
</script>
