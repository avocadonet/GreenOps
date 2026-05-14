<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center p-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold tracking-tight text-slate-800">
          GreenOps <span class="text-emerald-600">SmartCity</span>
        </h1>
        <p class="text-sm text-slate-500 mt-1">Energy Monitoring Platform</p>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4">
          {{ mode === 'login' ? 'Sign In' : 'Create Account' }}
        </h2>

        <div v-if="successMsg" class="mb-4 p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-sm text-emerald-700">
          {{ successMsg }}
        </div>
        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600">
          {{ error }}
        </div>

        <form @submit.prevent="submit" class="space-y-4">
          <div v-if="mode === 'register'">
            <label class="form-label">Full Name</label>
            <input v-model="form.fullname" class="form-input" placeholder="Jane Doe" />
          </div>
          <div>
            <label class="form-label">Email</label>
            <input v-model="form.email" type="email" required class="form-input" placeholder="you@example.com" />
          </div>
          <div>
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" required class="form-input" placeholder="••••••••" />
          </div>
          <button type="submit" :disabled="loading" class="btn-primary w-full">
            {{ loading ? 'Please wait…' : mode === 'login' ? 'Sign In' : 'Register' }}
          </button>
        </form>

        <p class="text-center text-sm text-slate-500 mt-4">
          {{ mode === 'login' ? "Don't have an account?" : 'Already have an account?' }}
          <button @click="toggleMode" class="text-emerald-600 font-semibold hover:underline ml-1">
            {{ mode === 'login' ? 'Register' : 'Sign In' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { authApi, usersApi, userRolesApi } from '../api/index.js';
import { useAuth } from '../composables/useAuth.js';

const { setAuth, setUserProfile } = useAuth();

const mode = ref('login');
const loading = ref(false);
const error = ref('');
const successMsg = ref('');
const form = ref({ email: '', password: '', fullname: '' });

const toggleMode = () => {
  mode.value = mode.value === 'login' ? 'register' : 'login';
  error.value = '';
  successMsg.value = '';
  form.value = { email: '', password: '', fullname: '' };
};

const submit = async () => {
  loading.value = true;
  error.value = '';
  successMsg.value = '';
  try {
    if (mode.value === 'login') {
      const { data } = await authApi.login({ email: form.value.email, password: form.value.password });
      setAuth(data);
      try {
        const [{ data: meData }, { data: rolesData }] = await Promise.all([
          usersApi.me(),
          userRolesApi.list(data.user_id),
        ]);
        setUserProfile(meData, rolesData);
      } catch {
        // login still succeeds; user gets PUBLIC-level access
      }
    } else {
      const { data } = await authApi.register(form.value);
      successMsg.value = data.message || 'Registered. Please wait for account activation before signing in.';
      mode.value = 'login';
      form.value = { email: form.value.email, password: '', fullname: '' };
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Something went wrong. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>
