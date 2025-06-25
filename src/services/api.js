import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for document processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Service Class
class APIService {
  // Document Management
  async uploadDocuments(files) {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getDocuments() {
    const response = await api.get('/documents');
    return response.data;
  }

  async getDocumentInfo(filename) {
    const response = await api.get(`/documents/${filename}/info`);
    return response.data;
  }

  async downloadDocument(filename) {
    const response = await api.get(`/documents/${filename}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async getDocumentBase64(filename) {
    const response = await api.get(`/documents/${filename}/base64`);
    return response.data;
  }

  async clearDocuments() {
    const response = await api.post('/documents/clear');
    return response.data;
  }

  // RAG Operations
  async queryDocuments(query, includeHtml = true) {
    const response = await api.post('/query', {
      query,
      include_html: includeHtml,
    });
    return response.data;
  }

  // Citation Navigation
  async getCitationNavigation(sourceNum, navType = 'web') {
    const response = await api.get(`/citations/${sourceNum}/navigate`, {
      params: { nav_type: navType },
    });
    return response.data;
  }

  // Health Check
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  }
}

// Export singleton instance
export const apiService = new APIService();
export default apiService; 