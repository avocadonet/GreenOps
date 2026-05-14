import { ref, computed } from 'vue';

const token = ref(localStorage.getItem('greenops_token') || '');
const user = ref(JSON.parse(localStorage.getItem('greenops_user') || 'null'));
const orgRoles = ref(JSON.parse(localStorage.getItem('greenops_org_roles') || '[]'));

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value);

  const setAuth = (data) => {
    token.value = data.access_token;
    user.value = { user_id: data.user_id, email: data.email, role: 'PUBLIC' };
    localStorage.setItem('greenops_token', data.access_token);
    localStorage.setItem('greenops_user', JSON.stringify(user.value));
  };

  const setUserProfile = (userData, rolesData) => {
    user.value = { ...user.value, role: userData.role };
    orgRoles.value = rolesData;
    localStorage.setItem('greenops_user', JSON.stringify(user.value));
    localStorage.setItem('greenops_org_roles', JSON.stringify(rolesData));
  };

  const logout = () => {
    token.value = '';
    user.value = null;
    orgRoles.value = [];
    localStorage.removeItem('greenops_token');
    localStorage.removeItem('greenops_user');
    localStorage.removeItem('greenops_org_roles');
  };

  return { token, user, orgRoles, isAuthenticated, setAuth, setUserProfile, logout };
}
