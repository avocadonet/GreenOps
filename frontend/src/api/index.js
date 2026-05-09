import axios from 'axios';
import { useAuth } from '../composables/useAuth.js';

const http = axios.create({ baseURL: '/api/v1' });

http.interceptors.request.use((config) => {
  const { token } = useAuth();
  if (token.value) {
    config.headers.Authorization = `Bearer ${token.value}`;
  }
  return config;
});

http.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const { logout } = useAuth();
      logout();
    }
    return Promise.reject(err);
  }
);

export const authApi = {
  login: (data) => http.post('/auth/login', data),
  register: (data) => http.post('/auth/register', data),
};

export const organizationsApi = {
  list: (params) => http.get('/organizations', { params }),
  create: (data) => http.post('/organizations', data),
  get: (id) => http.get(`/organizations/${id}`),
  update: (id, data) => http.put(`/organizations/${id}`, data),
  remove: (id) => http.delete(`/organizations/${id}`),
};

export const buildingsApi = {
  list: (params) => http.get('/buildings', { params }),
  create: (data) => http.post('/buildings', data),
  get: (id) => http.get(`/buildings/${id}`),
  update: (id, data) => http.put(`/buildings/${id}`, data),
  remove: (id) => http.delete(`/buildings/${id}`),
};

export const unitsApi = {
  list: (params) => http.get('/units', { params }),
  create: (data) => http.post('/units', data),
  get: (id) => http.get(`/units/${id}`),
  update: (id, data) => http.put(`/units/${id}`, data),
  remove: (id) => http.delete(`/units/${id}`),
};

export const sensorsApi = {
  list: (params) => http.get('/sensors', { params }),
  create: (data) => http.post('/sensors', data),
  get: (id) => http.get(`/sensors/${id}`),
  remove: (id) => http.delete(`/sensors/${id}`),
};

export const thresholdsApi = {
  list: (params) => http.get('/thresholds', { params }),
  create: (data) => http.post('/thresholds', data),
  get: (id) => http.get(`/thresholds/${id}`),
  remove: (id) => http.delete(`/thresholds/${id}`),
};

export const energyBalancesApi = {
  list: (params) => http.get('/energy-balances', { params }),
};
