import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { EquipmentCard } from './EquipmentCard'
import type { Tractor, Combine, Implement } from '../lib/mockApi'

describe('EquipmentCard', () => {
  describe('Tractor', () => {
    const tractor: Tractor = {
      make: 'John Deere',
      model: '5075E',
      category: 'tractor',
      series: '5E Series',
      year_start: 2014,
      year_end: 2023,
      pto_hp: 65,
      engine_hp: 75,
      transmission_type: 'powershift',
      description: 'Test tractor description',
    }

    it('should render tractor make and model', () => {
      render(<EquipmentCard equipment={tractor} />)
      expect(screen.getByText(/John Deere 5075E/i)).toBeInTheDocument()
    })

    it('should render category badge', () => {
      render(<EquipmentCard equipment={tractor} />)
      expect(screen.getByText('tractor')).toBeInTheDocument()
    })

    it('should render series', () => {
      render(<EquipmentCard equipment={tractor} />)
      expect(screen.getByText('5E Series')).toBeInTheDocument()
    })

    it('should render description', () => {
      render(<EquipmentCard equipment={tractor} />)
      expect(screen.getByText('Test tractor description')).toBeInTheDocument()
    })

    it('should render year range', () => {
      render(<EquipmentCard equipment={tractor} />)
      expect(screen.getByText(/2014.*2023/)).toBeInTheDocument()
    })

    it('should render PTO HP', () => {
      render(<EquipmentCard equipment={tractor} />)
      expect(screen.getByText('PTO HP:')).toBeInTheDocument()
      expect(screen.getByText('65')).toBeInTheDocument()
    })

    it('should render engine HP', () => {
      render(<EquipmentCard equipment={tractor} />)
      expect(screen.getByText('Engine HP:')).toBeInTheDocument()
      expect(screen.getByText('75')).toBeInTheDocument()
    })

    it('should render transmission type', () => {
      render(<EquipmentCard equipment={tractor} />)
      expect(screen.getByText('Transmission:')).toBeInTheDocument()
      expect(screen.getByText('powershift')).toBeInTheDocument()
    })
  })

  describe('Combine', () => {
    const combine: Combine = {
      make: 'Case IH',
      model: 'Axial-Flow 9250',
      category: 'combine',
      series: 'Axial-Flow 50 Series',
      year_start: 2020,
      grain_tank_capacity: 460,
      separator_type: 'rotary',
      engine_hp: 625,
      description: 'Test combine description',
    }

    it('should render combine make and model', () => {
      render(<EquipmentCard equipment={combine} />)
      expect(screen.getByText(/Case IH Axial-Flow 9250/i)).toBeInTheDocument()
    })

    it('should render grain tank capacity', () => {
      render(<EquipmentCard equipment={combine} />)
      expect(screen.getByText('Tank Capacity:')).toBeInTheDocument()
      expect(screen.getByText(/460 bu/)).toBeInTheDocument()
    })

    it('should render separator type', () => {
      render(<EquipmentCard equipment={combine} />)
      expect(screen.getByText('Separator:')).toBeInTheDocument()
      expect(screen.getByText('rotary')).toBeInTheDocument()
    })

    it('should render engine HP', () => {
      render(<EquipmentCard equipment={combine} />)
      expect(screen.getByText('Engine HP:')).toBeInTheDocument()
      expect(screen.getByText('625')).toBeInTheDocument()
    })
  })

  describe('Implement', () => {
    const implement: Implement = {
      make: 'Great Plains',
      model: 'YP-1625A',
      category: 'implement',
      series: 'Yield-Pro',
      year_start: 2020,
      working_width: 25,
      hp_required_min: 200,
      hp_required_max: 300,
      description: 'Test implement description',
    }

    it('should render implement make and model', () => {
      render(<EquipmentCard equipment={implement} />)
      expect(screen.getByText(/Great Plains YP-1625A/i)).toBeInTheDocument()
    })

    it('should render working width', () => {
      render(<EquipmentCard equipment={implement} />)
      expect(screen.getByText('Width:')).toBeInTheDocument()
      expect(screen.getByText(/25 ft/)).toBeInTheDocument()
    })

    it('should render HP required range', () => {
      render(<EquipmentCard equipment={implement} />)
      expect(screen.getByText('HP Required:')).toBeInTheDocument()
      expect(screen.getByText(/200.*300/)).toBeInTheDocument()
    })
  })

  describe('Minimal equipment', () => {
    it('should render equipment with only required fields', () => {
      const minimalEquipment = {
        make: 'Test Make',
        model: 'Test Model',
        category: 'tractor' as const,
      }

      render(<EquipmentCard equipment={minimalEquipment} />)
      expect(screen.getByText(/Test Make Test Model/i)).toBeInTheDocument()
      expect(screen.getByText('tractor')).toBeInTheDocument()
    })
  })
})
