import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest'
import { api } from './api'

// Mock fetch globally for tests
// @ts-expect-error - global is available in test environment
global.fetch = vi.fn()

describe('api', () => {
  beforeAll(() => {
    // Mock API responses
    vi.mocked(fetch).mockImplementation((url) => {
      const urlString = url.toString()
      
      if (urlString.includes('/equipment/tractors')) {
        return Promise.resolve({
          ok: true,
          json: async () => [],
        } as Response)
      }
      
      if (urlString.includes('/equipment/combines')) {
        return Promise.resolve({
          ok: true,
          json: async () => [],
        } as Response)
      }
      
      if (urlString.includes('/equipment/implements')) {
        return Promise.resolve({
          ok: true,
          json: async () => [],
        } as Response)
      }
      
      if (urlString.includes('/equipment')) {
        return Promise.resolve({
          ok: true,
          json: async () => [],
        } as Response)
      }
      
      if (urlString.includes('/stats')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            total_equipment: 0,
            tractors: 0,
            combines: 0,
            implements: 0,
          }),
        } as Response)
      }
      
      return Promise.resolve({
        ok: false,
        statusText: 'Not Found',
      } as Response)
    })
  })

  afterAll(() => {
    vi.restoreAllMocks()
  })

  describe('getAllEquipment', () => {
    it('should call the correct endpoint', async () => {
      await api.getAllEquipment()
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/equipment'))
    })

    it('should return an array', async () => {
      const equipment = await api.getAllEquipment()
      expect(Array.isArray(equipment)).toBe(true)
    })
  })

  describe('getEquipmentByCategory', () => {
    it('should include category in query string', async () => {
      await api.getEquipmentByCategory('tractor')
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/equipment?category=tractor')
      )
    })
  })

  describe('getTractors', () => {
    it('should call the tractors endpoint', async () => {
      await api.getTractors()
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/equipment/tractors'))
    })
  })

  describe('getCombines', () => {
    it('should call the combines endpoint', async () => {
      await api.getCombines()
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/equipment/combines'))
    })
  })

  describe('getImplements', () => {
    it('should call the implements endpoint', async () => {
      await api.getImplements()
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/equipment/implements'))
    })
  })

  describe('getStats', () => {
    it('should call the stats endpoint', async () => {
      await api.getStats()
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/stats'))
    })

    it('should return statistics object', async () => {
      const stats = await api.getStats()
      expect(stats).toHaveProperty('total_equipment')
      expect(stats).toHaveProperty('tractors')
      expect(stats).toHaveProperty('combines')
      expect(stats).toHaveProperty('implements')
    })
  })

  describe('error handling', () => {
    it('should throw error on failed request', async () => {
      vi.mocked(fetch).mockImplementationOnce(() =>
        Promise.resolve({
          ok: false,
          statusText: 'Internal Server Error',
        } as Response)
      )

      await expect(api.getAllEquipment()).rejects.toThrow()
    })
  })
})
