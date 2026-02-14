// API Adapter - Automatically switches between real API and mock API based on environment
// In production (GitHub Pages), use mock data
// In development, use real backend API

import { api, Equipment, Stats } from './api';
import { mockApi } from './mockApi';

// Detect if running in production (GitHub Pages) or development
const isProduction = import.meta.env.PROD && !import.meta.env.VITE_API_URL;

// Export the appropriate API client based on environment
export const apiClient = {
  async getAllEquipment(): Promise<Equipment[]> {
    if (isProduction) {
      return mockApi.getAllEquipment();
    }
    try {
      return await api.getAllEquipment();
    } catch (error) {
      console.warn('Failed to fetch from real API, falling back to mock data:', error);
      return mockApi.getAllEquipment();
    }
  },

  async getEquipmentByCategory(category: string): Promise<Equipment[]> {
    if (isProduction) {
      return mockApi.getEquipmentByCategory(category);
    }
    try {
      return await api.getEquipmentByCategory(category);
    } catch (error) {
      console.warn('Failed to fetch from real API, falling back to mock data:', error);
      return mockApi.getEquipmentByCategory(category);
    }
  },

  async getTractors(): Promise<Equipment[]> {
    if (isProduction) {
      return mockApi.getTractors();
    }
    try {
      return await api.getTractors();
    } catch (error) {
      console.warn('Failed to fetch from real API, falling back to mock data:', error);
      return mockApi.getTractors();
    }
  },

  async getCombines(): Promise<Equipment[]> {
    if (isProduction) {
      return mockApi.getCombines();
    }
    try {
      return await api.getCombines();
    } catch (error) {
      console.warn('Failed to fetch from real API, falling back to mock data:', error);
      return mockApi.getCombines();
    }
  },

  async getImplements(): Promise<Equipment[]> {
    if (isProduction) {
      return mockApi.getImplements();
    }
    try {
      return await api.getImplements();
    } catch (error) {
      console.warn('Failed to fetch from real API, falling back to mock data:', error);
      return mockApi.getImplements();
    }
  },

  async searchEquipment(query: string): Promise<Equipment[]> {
    if (isProduction) {
      return mockApi.searchEquipment(query);
    }
    try {
      return await api.searchEquipment(query);
    } catch (error) {
      console.warn('Failed to search from real API, falling back to mock data:', error);
      return mockApi.searchEquipment(query);
    }
  },

  async getStats(): Promise<Stats> {
    if (isProduction) {
      return mockApi.getStats();
    }
    try {
      return await api.getStats();
    } catch (error) {
      console.warn('Failed to fetch stats from real API, falling back to mock data:', error);
      return mockApi.getStats();
    }
  },
};

// Export flag to indicate if using mock data
export const isUsingMockData = isProduction;
