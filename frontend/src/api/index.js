import axios from 'axios';

const http = axios.create({ baseURL: '/api/v1' });

export const buildingsApi = {
  create: (data) => http.post('/buildings', data),
  get: (id) => http.get(`/buildings/${id}`),
  update: (id, data) => http.put(`/buildings/${id}`, data),
  remove: (id) => http.delete(`/buildings/${id}`),
};

export const unitsApi = {
  create: (data) => http.post('/units', data),
  get: (id) => http.get(`/units/${id}`),
  update: (id, data) => http.put(`/units/${id}`, data),
  remove: (id) => http.delete(`/units/${id}`),
};

export const sensorsApi = {
  create: (data) => http.post('/sensors', data),
  get: (id) => http.get(`/sensors/${id}`),
  remove: (id) => http.delete(`/sensors/${id}`),
};

export const thresholdsApi = {
  create: (data) => http.post('/thresholds', data),
  get: (id) => http.get(`/thresholds/${id}`),
  remove: (id) => http.delete(`/thresholds/${id}`),
};

export const analyticsApi = {
  current: (buildingId) => http.get(`/analytics/${buildingId}/current`),
  history: (buildingId) => http.get(`/analytics/${buildingId}/history`),
};
