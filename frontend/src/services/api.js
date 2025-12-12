import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Methods
export const predictGuard = async (data) => {
  const response = await api.post('/predict', data);
  return response.data;
};

export const analyzeCounterfactual = async (data) => {
  const response = await api.post('/counterfactual', data);
  return response.data;
};

export const explainPrediction = async (data) => {
  const response = await api.post('/explain', data);
  return response.data;
};

export const getFeatureImportance = async (modelId) => {
  const response = await api.get(`/feature-importance/${modelId}`);
  return response.data;
};

export const listModels = async () => {
  const response = await api.get('/models');
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
