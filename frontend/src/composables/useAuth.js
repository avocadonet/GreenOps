import { ref, computed } from 'vue';

const token = ref(localStorage.getItem('greenops_token') || '');
const user = ref(JSON.parse(localStorage.getItem('greenops_user') || 'null'));

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value);

  const setAuth = (data) => {
    token.value = data.access_token;
    user.value = { user_id: data.user_id, email: data.email };
    localStorage.setItem('greenops_token', data.access_token);
    localStorage.setItem('greenops_user', JSON.stringify(user.value));
  };

  const logout = () => {
    token.value = '';
    user.value = null;
    localStorage.removeItem('greenops_token');
    localStorage.removeItem('greenops_user');
  };

  return { token, user, isAuthenticated, setAuth, logout };
}
