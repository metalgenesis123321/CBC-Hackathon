// src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Send a chat message to the backend
 * @param {string} query - User's question/message
 * @param {string|null} marketId - Optional market ID for dashboard generation
 * @returns {Promise} Response with type (chat/dashboard/error) and data
 */
export const sendMessage = async (query, marketId = null) => {
  try {
    const payload = {
      query: query.trim(),
    };

    if (marketId) {
      payload.market_id = marketId;
    }

    const response = await apiClient.post('/chat', payload);
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    
    // Return error in consistent format
    return {
      type: 'error',
      message: error.response?.data?.detail || 
               error.message || 
               'Failed to connect to the server. Please try again.',
    };
  }
};

/**
 * Get dashboard data directly for a market
 * @param {string} marketId - Market ID
 * @returns {Promise} Dashboard data
 */
export const getDashboard = async (marketId) => {
  try {
    const response = await apiClient.get('/dashboard', {
      params: { market_id: marketId },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard:', error);
    throw error;
  }
};

/**
 * Check API health
 * @returns {Promise} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    return { ok: false, error: error.message };
  }
};

/**
 * Get API info
 * @returns {Promise} API information
 */
export const getApiInfo = async () => {
  try {
    const response = await apiClient.get('/');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch API info:', error);
    return null;
  }
};

export default {
  sendMessage,
  getDashboard,
  checkHealth,
  getApiInfo,
};