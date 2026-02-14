// API Adapter - Automatically switches between real API and mock API based on environment
// In production (GitHub Pages), use mock data
// In development, use real backend API

import { api, Equipment, Stats } from './api';
import { mockApi } from './mockApi';

// Detect if running in production (GitHub Pages) or development
const isProduction = import.meta.env.PROD && !import.meta.env.VITE_API_URL;

// Higher-order function to handle API calls with fallback
async function withFallback<T>(
  realApiFn: () => Promise<T>,
  mockApiFn: () => Promise<T>,
  errorMessage: string
): Promise<T> {
  if (isProduction) {
    return mockApiFn();
  }
  try {
    return await realApiFn();
  } catch (error) {
    console.warn(`${errorMessage}:`, error);
    return mockApiFn();
  }
}

// Export the appropriate API client based on environment
export const apiClient = {
  async getAllEquipment(): Promise<Equipment[]> {
    return withFallback(
      () => api.getAllEquipment(),
      () => mockApi.getAllEquipment(),
      'Failed to fetch from real API, falling back to mock data'
    );
  },

  async getEquipmentByCategory(category: string): Promise<Equipment[]> {
    return withFallback(
      () => api.getEquipmentByCategory(category),
      () => mockApi.getEquipmentByCategory(category),
      'Failed to fetch from real API, falling back to mock data'
    );
  },

  async getTractors(): Promise<Equipment[]> {
    return withFallback(
      () => api.getTractors(),
      () => mockApi.getTractors(),
      'Failed to fetch from real API, falling back to mock data'
    );
  },

  async getCombines(): Promise<Equipment[]> {
    return withFallback(
      () => api.getCombines(),
      () => mockApi.getCombines(),
      'Failed to fetch from real API, falling back to mock data'
    );
  },

  async getImplements(): Promise<Equipment[]> {
    return withFallback(
      () => api.getImplements(),
      () => mockApi.getImplements(),
      'Failed to fetch from real API, falling back to mock data'
    );
  },

  async searchEquipment(query: string): Promise<Equipment[]> {
    return withFallback(
      () => api.searchEquipment(query),
      () => mockApi.searchEquipment(query),
      'Failed to search from real API, falling back to mock data'
    );
  },

  async getStats(): Promise<Stats> {
    return withFallback(
      () => api.getStats(),
      () => mockApi.getStats(),
      'Failed to fetch stats from real API, falling back to mock data'
    );
  },
};

// Export flag to indicate if using mock data
export const isUsingMockData = isProduction;
