import api from './api';

export const getGenerations = (params = {}) =>
  api.get('/generations', { params }).then((r) => r.data);

export const createGeneration = (data) =>
  api.post('/generations', data).then((r) => r.data);

export const generateDirect = (data) =>
  api.post('/generations/generate', data).then((r) => r.data);

export const getGeneration = (id) =>
  api.get(`/generations/${id}`).then((r) => r.data);

export const getGenerationStatus = (id) =>
  api.get(`/generations/${id}/status`).then((r) => r.data);

export const regenerateGeneration = (id, data) =>
  api.post(`/generations/${id}/regenerate`, data).then((r) => r.data);

export const scoreGeneration = (id) =>
  api.post(`/generations/${id}/score`).then((r) => r.data);

export const exportGeneration = (id, data) =>
  api.post(`/generations/${id}/export`, data).then((r) => r.data);

export const enhancePrompt = (data) =>
  api.post('/generations/ai/enhance-prompt', data).then((r) => r.data);

export const generateTitles = (data) =>
  api.post('/generations/ai/generate-title', data).then((r) => r.data);
