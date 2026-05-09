import api from './api';

export const getProjects = (page = 1, pageSize = 20) =>
  api.get('/projects', { params: { page, page_size: pageSize } }).then((r) => r.data);

export const getProject = (id) =>
  api.get(`/projects/${id}`).then((r) => r.data);

export const createProject = (data) =>
  api.post('/projects', data).then((r) => r.data);

export const updateProject = (id, data) =>
  api.put(`/projects/${id}`, data).then((r) => r.data);

export const deleteProject = (id) =>
  api.delete(`/projects/${id}`);

export const duplicateProject = (id) =>
  api.post(`/projects/${id}/duplicate`).then((r) => r.data);

export const getStyles = () =>
  api.get('/projects/styles').then((r) => r.data);

export const getTemplates = (category) =>
  api.get('/projects/templates', { params: { category } }).then((r) => r.data);
