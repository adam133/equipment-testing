import { describe, it, expect } from 'vitest'
import { mockApi } from '../lib/mockApi'

describe('mockApi', () => {
  describe('getAllEquipment', () => {
    it('should return all equipment', async () => {
      const equipment = await mockApi.getAllEquipment()
      expect(equipment).toBeDefined()
      expect(equipment.length).toBeGreaterThan(0)
    })

    it('should include tractors, combines, and implements', async () => {
      const equipment = await mockApi.getAllEquipment()
      const categories = equipment.map(item => item.category)
      expect(categories).toContain('tractor')
      expect(categories).toContain('combine')
      expect(categories).toContain('implement')
    })
  })

  describe('getEquipmentByCategory', () => {
    it('should filter by tractor category', async () => {
      const tractors = await mockApi.getEquipmentByCategory('tractor')
      expect(tractors.length).toBeGreaterThan(0)
      tractors.forEach(item => {
        expect(item.category).toBe('tractor')
      })
    })

    it('should filter by combine category', async () => {
      const combines = await mockApi.getEquipmentByCategory('combine')
      expect(combines.length).toBeGreaterThan(0)
      combines.forEach(item => {
        expect(item.category).toBe('combine')
      })
    })

    it('should filter by implement category', async () => {
      const implementResults = await mockApi.getEquipmentByCategory('implement')
      expect(implementResults.length).toBeGreaterThan(0)
      implementResults.forEach(item => {
        expect(item.category).toBe('implement')
      })
    })
  })

  describe('getTractors', () => {
    it('should return only tractors', async () => {
      const tractors = await mockApi.getTractors()
      expect(tractors.length).toBeGreaterThan(0)
      tractors.forEach(tractor => {
        expect(tractor.category).toBe('tractor')
        expect(tractor).toHaveProperty('make')
        expect(tractor).toHaveProperty('model')
      })
    })
  })

  describe('getCombines', () => {
    it('should return only combines', async () => {
      const combines = await mockApi.getCombines()
      expect(combines.length).toBeGreaterThan(0)
      combines.forEach(combine => {
        expect(combine.category).toBe('combine')
      })
    })
  })

  describe('getImplements', () => {
    it('should return only implements', async () => {
      const implementResults = await mockApi.getImplements()
      expect(implementResults.length).toBeGreaterThan(0)
      implementResults.forEach(implement => {
        expect(implement.category).toBe('implement')
      })
    })
  })

  describe('searchEquipment', () => {
    it('should find equipment by make', async () => {
      const results = await mockApi.searchEquipment('John Deere')
      expect(results.length).toBeGreaterThan(0)
      results.forEach(item => {
        expect(item.make.toLowerCase()).toContain('john deere'.toLowerCase())
      })
    })

    it('should find equipment by model', async () => {
      const results = await mockApi.searchEquipment('5075E')
      expect(results.length).toBeGreaterThan(0)
      results.forEach(item => {
        expect(item.model.toLowerCase()).toContain('5075e'.toLowerCase())
      })
    })

    it('should return empty array for no matches', async () => {
      const results = await mockApi.searchEquipment('nonexistent')
      expect(results).toEqual([])
    })

    it('should be case insensitive', async () => {
      const results = await mockApi.searchEquipment('JOHN DEERE')
      expect(results.length).toBeGreaterThan(0)
    })
  })

  describe('getStats', () => {
    it('should return statistics', async () => {
      const stats = await mockApi.getStats()
      expect(stats).toHaveProperty('total_equipment')
      expect(stats).toHaveProperty('tractors')
      expect(stats).toHaveProperty('combines')
      expect(stats).toHaveProperty('implements')
    })

    it('should have correct counts', async () => {
      const stats = await mockApi.getStats()
      expect(stats.total_equipment).toBeGreaterThan(0)
      expect(stats.total_equipment).toBe(
        stats.tractors + stats.combines + stats.implements
      )
    })
  })
})
