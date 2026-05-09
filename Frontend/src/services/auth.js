import api from './api';

export const login = (email, password) =>
  api.post('/auth/login', { email, password }).then((r) => r.data);

export const register = (email, password, name) =>
  api.post('/auth/register', { email, password, name }).then((r) => r.data);

export const getMe = () =>
  api.get('/auth/me').then((r) => r.data);

export const refreshToken = (refresh_token) =>
  api.post('/auth/refresh', { refresh_token }).then((r) => r.data);

export const logout = () =>
  api.post('/auth/logout');
