import api from './api';

export const uploadImage = (file, folder = 'general') => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/uploads/image', form, {
    params: { folder },
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((r) => r.data);
};

export const removeBackground = (imageUrl) =>
  api.post('/uploads/remove-background', null, { params: { image_url: imageUrl } }).then((r) => r.data);

export const enhanceImage = (imageUrl) =>
  api.post('/uploads/enhance', null, { params: { image_url: imageUrl } }).then((r) => r.data);
