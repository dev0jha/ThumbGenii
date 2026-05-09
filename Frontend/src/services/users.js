import api from './api';

export const getProfile = () =>
  api.get('/users/me').then((r) => r.data);

export const updateProfile = (data) =>
  api.put('/users/me', data).then((r) => r.data);

export const getPreferences = () =>
  api.get('/users/me/preferences').then((r) => r.data);

export const updatePreferences = (data) =>
  api.put('/users/me/preferences', data).then((r) => r.data);

export const getStats = () =>
  api.get('/users/me/stats').then((r) => r.data);

export const getAnalytics = () =>
  api.get('/users/me/analytics').then((r) => r.data);

export const changePassword = (current_password, new_password) =>
  api.post('/auth/change-password', { current_password, new_password }).then((r) => r.data);
