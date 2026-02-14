import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from './apiAdapter';
import * as mockApiModule from './mockApi';
import * as apiModule from './api';

// Mock the modules
vi.mock('./mockApi', () => ({
  mockApi: {
    getAllEquipment: vi.fn(),
    getEquipmentByCategory: vi.fn(),
    getTractors: vi.fn(),
    getCombines: vi.fn(),
    getImplements: vi.fn(),
    searchEquipment: vi.fn(),
    getStats: vi.fn(),
  },
}));

vi.mock('./api', () => ({
  api: {
    getAllEquipment: vi.fn(),
    getEquipmentByCategory: vi.fn(),
    getTractors: vi.fn(),
    getCombines: vi.fn(),
    getImplements: vi.fn(),
    searchEquipment: vi.fn(),
    getStats: vi.fn(),
  },
}));

describe('apiAdapter', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getAllEquipment', () => {
    it('should call real API in development', async () => {
      const mockData = [
        { make: 'Test', model: 'Model1', category: 'tractor' },
      ];
      vi.mocked(apiModule.api.getAllEquipment).mockResolvedValue(mockData);

      const result = await apiClient.getAllEquipment();

      expect(result).toEqual(mockData);
    });

    it('should fall back to mock API if real API fails', async () => {
      const mockData = [
        { make: 'Mock', model: 'Model1', category: 'tractor' },
      ];
      vi.mocked(apiModule.api.getAllEquipment).mockRejectedValue(
        new Error('API not available')
      );
      vi.mocked(mockApiModule.mockApi.getAllEquipment).mockResolvedValue(mockData);

      const result = await apiClient.getAllEquipment();

      expect(result).toEqual(mockData);
      expect(mockApiModule.mockApi.getAllEquipment).toHaveBeenCalled();
    });
  });

  describe('getStats', () => {
    it('should call real API in development', async () => {
      const mockStats = {
        total_equipment: 10,
        tractors: 5,
        combines: 3,
        implements: 2,
      };
      vi.mocked(apiModule.api.getStats).mockResolvedValue(mockStats);

      const result = await apiClient.getStats();

      expect(result).toEqual(mockStats);
    });

    it('should fall back to mock API if real API fails', async () => {
      const mockStats = {
        total_equipment: 8,
        tractors: 4,
        combines: 2,
        implements: 2,
      };
      vi.mocked(apiModule.api.getStats).mockRejectedValue(
        new Error('API not available')
      );
      vi.mocked(mockApiModule.mockApi.getStats).mockResolvedValue(mockStats);

      const result = await apiClient.getStats();

      expect(result).toEqual(mockStats);
      expect(mockApiModule.mockApi.getStats).toHaveBeenCalled();
    });
  });

  describe('getEquipmentByCategory', () => {
    it('should call real API with category parameter', async () => {
      const mockData = [
        { make: 'Test', model: 'Model1', category: 'tractor' },
      ];
      vi.mocked(apiModule.api.getEquipmentByCategory).mockResolvedValue(mockData);

      const result = await apiClient.getEquipmentByCategory('tractor');

      expect(result).toEqual(mockData);
      expect(apiModule.api.getEquipmentByCategory).toHaveBeenCalledWith('tractor');
    });

    it('should fall back to mock API if real API fails', async () => {
      const mockData = [
        { make: 'Mock', model: 'Model1', category: 'combine' },
      ];
      vi.mocked(apiModule.api.getEquipmentByCategory).mockRejectedValue(
        new Error('API not available')
      );
      vi.mocked(mockApiModule.mockApi.getEquipmentByCategory).mockResolvedValue(
        mockData
      );

      const result = await apiClient.getEquipmentByCategory('combine');

      expect(result).toEqual(mockData);
      expect(mockApiModule.mockApi.getEquipmentByCategory).toHaveBeenCalledWith(
        'combine'
      );
    });
  });

  describe('searchEquipment', () => {
    it('should call real API with search query', async () => {
      const mockData = [
        { make: 'John Deere', model: '8R 370', category: 'tractor' },
      ];
      vi.mocked(apiModule.api.searchEquipment).mockResolvedValue(mockData);

      const result = await apiClient.searchEquipment('John Deere');

      expect(result).toEqual(mockData);
      expect(apiModule.api.searchEquipment).toHaveBeenCalledWith('John Deere');
    });

    it('should fall back to mock API if real API fails', async () => {
      const mockData = [
        { make: 'Mock', model: 'Test', category: 'tractor' },
      ];
      vi.mocked(apiModule.api.searchEquipment).mockRejectedValue(
        new Error('API not available')
      );
      vi.mocked(mockApiModule.mockApi.searchEquipment).mockResolvedValue(mockData);

      const result = await apiClient.searchEquipment('test');

      expect(result).toEqual(mockData);
      expect(mockApiModule.mockApi.searchEquipment).toHaveBeenCalledWith('test');
    });
  });
});
