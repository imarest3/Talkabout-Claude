import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/auth/token/', { username, password }),

  register: (userData) =>
    api.post('/auth/users/', userData),

  getProfile: () =>
    api.get('/auth/users/me/'),

  updateProfile: (userData) =>
    api.put('/auth/users/update_profile/', userData),

  changePassword: (passwordData) =>
    api.post('/auth/users/change_password/', passwordData),

  logout: (refreshToken) =>
    api.post('/auth/users/logout/', { refresh_token: refreshToken }),
};

// Activities API
export const activitiesAPI = {
  getAll: (params) =>
    api.get('/activities/', { params }),

  getOne: (id) =>
    api.get(`/activities/${id}/`),

  create: (data) =>
    api.post('/activities/', data),

  update: (id, data) =>
    api.put(`/activities/${id}/`, data),

  delete: (id) =>
    api.delete(`/activities/${id}/`),

  uploadFile: (id, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/activities/${id}/upload_file/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  getFiles: (id) =>
    api.get(`/activities/${id}/files/`),
};

// Events API
export const eventsAPI = {
  getAll: (params) =>
    api.get('/events/', { params }),

  getOne: (id) =>
    api.get(`/events/${id}/`),

  create: (data) =>
    api.post('/events/', data),

  update: (id, data) =>
    api.put(`/events/${id}/`, data),

  delete: (id) =>
    api.delete(`/events/${id}/`),

  getEnrollments: (id) =>
    api.get(`/events/${id}/enrollments/`),
};

// Enrollments API
export const enrollmentsAPI = {
  getAll: (params) =>
    api.get('/enrollments/', { params }),

  getMy: (params) =>
    api.get('/enrollments/my_enrollments/', { params }),

  enroll: (eventId) =>
    api.post('/enrollments/', { event: eventId }),

  cancel: (id) =>
    api.post(`/enrollments/${id}/cancel/`),
};

// Meetings API
export const meetingsAPI = {
  getAll: (params) =>
    api.get('/meetings/', { params }),

  getOne: (id) =>
    api.get(`/meetings/${id}/`),

  join: (id) =>
    api.post(`/meetings/${id}/join/`),

  leave: (id) =>
    api.post(`/meetings/${id}/leave/`),
};

// Statistics API
export const statisticsAPI = {
  getActivities: () =>
    api.get('/statistics/activities/'),

  getEvents: (params) =>
    api.get('/statistics/events/', { params }),

  getUsers: () =>
    api.get('/statistics/users/'),

  getMyStats: () =>
    api.get('/statistics/my_stats/'),
};

export default api;
