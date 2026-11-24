import axios from 'axios';

// Environment-aware API Base URL resolution
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

// Unified Axios Client Instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor for Zero Trust Bearer Token Injection
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('easymail_auth_token') || localStorage.getItem('easymail_jwt');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth Endpoints
export const fetchCurrentUser = async () => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};

// Email Feed Endpoints
export const fetchInbox = async (query = 'in:inbox') => {
  const response = await apiClient.get('/email/messages', { params: { q: query } });
  return response.data;
};

export const fetchThread = async (threadId) => {
  const response = await apiClient.get(`/email/threads/${encodeURIComponent(threadId)}`);
  return response.data;
};

export const sendEmail = async (payload) => {
  const response = await apiClient.post('/email/send', payload);
  return response.data;
};

export const createDraft = async (payload) => {
  const response = await apiClient.post('/email/drafts', payload);
  return response.data;
};

export const toggleStar = async (messageId, starred) => {
  const response = await apiClient.post(`/email/messages/${encodeURIComponent(messageId)}/labels`, {
    add_label_ids: starred ? ['STARRED'] : [],
    remove_label_ids: starred ? [] : ['STARRED'],
  });
  return response.data;
};

export const trashMessage = async (messageId) => {
  const response = await apiClient.post(`/email/messages/${encodeURIComponent(messageId)}/trash`);
  return response.data;
};

// AI & Microservice Endpoints
export const analyzeEmailThreat = async (messagePayload) => {
  const response = await apiClient.post('/threats/analyze', messagePayload);
  return response.data;
};

export const summarizeThread = async (threadId, messageBodies) => {
  const response = await apiClient.post('/ai/summarize', {
    thread_id: threadId,
    message_bodies: messageBodies,
  });
  return response.data;
};

export const fetchSmartCompose = async (subject, bodyPrefix = '') => {
  const response = await apiClient.post('/ai/smart-compose', {
    subject,
    body_prefix: bodyPrefix,
  });
  return response.data;
};

export const quarantineThreat = async (messageId) => {
  const response = await apiClient.post(`/threats/quarantine/${encodeURIComponent(messageId)}`);
  return response.data;
};

export const markThreatSafe = async (messageId) => {
  const response = await apiClient.post(`/threats/mark-safe/${encodeURIComponent(messageId)}`);
  return response.data;
};