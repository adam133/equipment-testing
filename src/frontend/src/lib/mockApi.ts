// Mock equipment data for frontend development
// This file provides hardcoded data to simulate the backend API

export interface Equipment {
  make: string;
  model: string;
  category: string;
  series?: string;
  year_start?: number;
  year_end?: number;
  description?: string;
  image_url?: string;
}

export interface Tractor extends Equipment {
  category: 'tractor';
  pto_hp?: number;
  engine_hp?: number;
  transmission_type?: string;
  weight_lbs?: number;
}

export interface Combine extends Equipment {
  category: 'combine';
  grain_tank_capacity?: number;
  separator_type?: string;
  engine_hp?: number;
}

export interface Implement extends Equipment {
  category: 'implement';
  working_width?: number;
  weight_lbs?: number;
  hp_required_min?: number;
  hp_required_max?: number;
}

export interface ErrorRecord {
  id: string;
  category: 'tractor' | 'combine' | 'implement';
  error_type: string;
  error_message: string;
  make?: string;
  model?: string;
  data: Record<string, any>;
}

// Mock data for tractors
const mockTractors: Tractor[] = [
  {
    make: 'John Deere',
    model: '5075E',
    category: 'tractor',
    series: '5E Series',
    year_start: 2014,
    year_end: 2023,
    pto_hp: 65,
    engine_hp: 75,
    transmission_type: 'powershift',
    weight_lbs: 7200,
    description: 'Utility tractor ideal for livestock, dairy, and general farming operations',
  },
  {
    make: 'John Deere',
    model: '8R 370',
    category: 'tractor',
    series: '8R Series',
    year_start: 2019,
    pto_hp: 320,
    engine_hp: 370,
    transmission_type: 'ivt',
    weight_lbs: 31000,
    description: 'High-horsepower row crop tractor with AutoTrac guidance',
  },
  {
    make: 'Case IH',
    model: 'Farmall 75C',
    category: 'tractor',
    series: 'Farmall C Series',
    year_start: 2018,
    pto_hp: 62,
    engine_hp: 75,
    transmission_type: 'powershift',
    weight_lbs: 7500,
    description: 'Versatile utility tractor for hay, livestock, and mixed farming',
  },
  {
    make: 'New Holland',
    model: 'T7.270',
    category: 'tractor',
    series: 'T7 Series',
    year_start: 2020,
    pto_hp: 235,
    engine_hp: 270,
    transmission_type: 'cvt',
    weight_lbs: 25000,
    description: 'High-performance tractor with Auto Command CVT transmission',
  },
  {
    make: 'Kubota',
    model: 'M7-172',
    category: 'tractor',
    series: 'M7 Series',
    year_start: 2017,
    pto_hp: 141,
    engine_hp: 172,
    transmission_type: 'cvt',
    weight_lbs: 17500,
    description: 'Mid-size tractor with advanced hydraulics and comfort',
  },
];

// Mock data for combines
const mockCombines: Combine[] = [
  {
    make: 'John Deere',
    model: 'S790',
    category: 'combine',
    series: 'S Series',
    year_start: 2017,
    grain_tank_capacity: 450,
    separator_type: 'rotary',
    engine_hp: 543,
    description: 'High-capacity combine with ProDrive transmission',
  },
  {
    make: 'Case IH',
    model: 'Axial-Flow 9250',
    category: 'combine',
    series: 'Axial-Flow 50 Series',
    year_start: 2020,
    grain_tank_capacity: 460,
    separator_type: 'rotary',
    engine_hp: 625,
    description: 'Flagship combine with twin rotors and high throughput',
  },
  {
    make: 'New Holland',
    model: 'CR10.90',
    category: 'combine',
    series: 'CR Revelation',
    year_start: 2019,
    grain_tank_capacity: 450,
    separator_type: 'rotary',
    engine_hp: 652,
    description: 'Top-of-line combine with Dynamic Feed Roll',
  },
];

// Mock data for implements
const mockImplements: Implement[] = [
  {
    make: 'John Deere',
    model: '2730',
    category: 'implement',
    series: 'Combination Ripper',
    year_start: 2015,
    working_width: 30,
    weight_lbs: 12000,
    hp_required_min: 300,
    hp_required_max: 450,
    description: 'Heavy-duty combination ripper for deep tillage',
  },
  {
    make: 'Case IH',
    model: 'Precision Disk 500T',
    category: 'implement',
    series: 'Precision Disk',
    year_start: 2018,
    working_width: 40,
    weight_lbs: 18000,
    hp_required_min: 250,
    hp_required_max: 400,
    description: 'High-speed vertical tillage tool',
  },
  {
    make: 'Great Plains',
    model: 'YP-1625A',
    category: 'implement',
    series: 'Yield-Pro',
    year_start: 2020,
    working_width: 25,
    weight_lbs: 15000,
    hp_required_min: 200,
    hp_required_max: 300,
    description: '16-row planter with precision seed placement',
  },
];

// Combine all mock data
const mockEquipment: Equipment[] = [
  ...mockTractors,
  ...mockCombines,
  ...mockImplements,
];

// Mock error records
const mockErrorRecords: ErrorRecord[] = [
  {
    id: 'err_001',
    category: 'tractor',
    error_type: 'ValidationError',
    error_message: 'Field required: year_start',
    make: 'John Deere',
    model: '6155R',
    data: {
      make: 'John Deere',
      model: '6155R',
      category: 'tractor',
      pto_hp: 155,
      engine_hp: 170,
      // year_start is missing
    },
  },
  {
    id: 'err_002',
    category: 'combine',
    error_type: 'ValidationError',
    error_message: 'Invalid value for separator_type: must be one of [conventional, rotary, hybrid]',
    make: 'Case IH',
    model: 'Axial-Flow 6150',
    data: {
      make: 'Case IH',
      model: 'Axial-Flow 6150',
      category: 'combine',
      separator_type: 'unknown',
      engine_hp: 353,
    },
  },
  {
    id: 'err_003',
    category: 'implement',
    error_type: 'ValueError',
    error_message: 'working_width must be positive',
    make: 'Great Plains',
    model: 'Turbo-Max 1500',
    data: {
      make: 'Great Plains',
      model: 'Turbo-Max 1500',
      category: 'implement',
      working_width: -15,
      weight_lbs: 8000,
    },
  },
  {
    id: 'err_004',
    category: 'tractor',
    error_type: 'ValidationError',
    error_message: 'year_end must be >= year_start',
    make: 'New Holland',
    model: 'T6.180',
    data: {
      make: 'New Holland',
      model: 'T6.180',
      category: 'tractor',
      year_start: 2020,
      year_end: 2018,
      pto_hp: 150,
    },
  },
  {
    id: 'err_005',
    category: 'combine',
    error_type: 'ValidationError',
    error_message: 'Field required: make',
    make: undefined,
    model: 'CR9.90',
    data: {
      model: 'CR9.90',
      category: 'combine',
      grain_tank_capacity: 460,
      engine_hp: 652,
    },
  },
  {
    id: 'err_006',
    category: 'tractor',
    error_type: 'TypeError',
    error_message: 'pto_hp must be a number',
    make: 'Kubota',
    model: 'M5-111',
    data: {
      make: 'Kubota',
      model: 'M5-111',
      category: 'tractor',
      pto_hp: 'N/A',
      engine_hp: 111,
    },
  },
  {
    id: 'err_007',
    category: 'implement',
    error_type: 'ValidationError',
    error_message: 'hp_required_max must be >= hp_required_min',
    make: 'John Deere',
    model: '2623VT',
    data: {
      make: 'John Deere',
      model: '2623VT',
      category: 'implement',
      working_width: 23,
      hp_required_min: 200,
      hp_required_max: 150,
    },
  },
  {
    id: 'err_008',
    category: 'tractor',
    error_type: 'ValidationError',
    error_message: 'Invalid transmission_type: must be one of [manual, powershift, cvt, hydrostatic, ivt, other]',
    make: 'Case IH',
    model: 'Maxxum 145',
    data: {
      make: 'Case IH',
      model: 'Maxxum 145',
      category: 'tractor',
      transmission_type: 'automatic',
      pto_hp: 125,
    },
  },
];

// Mock API client functions
export const mockApi = {
  // Get all equipment
  async getAllEquipment(): Promise<Equipment[]> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockEquipment;
  },

  // Get equipment by category
  async getEquipmentByCategory(category: string): Promise<Equipment[]> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockEquipment.filter(item => item.category === category);
  },

  // Get tractors
  async getTractors(): Promise<Tractor[]> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockTractors;
  },

  // Get combines
  async getCombines(): Promise<Combine[]> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockCombines;
  },

  // Get implements
  async getImplements(): Promise<Implement[]> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockImplements;
  },

  // Search equipment
  async searchEquipment(query: string): Promise<Equipment[]> {
    await new Promise(resolve => setTimeout(resolve, 300));
    const lowerQuery = query.toLowerCase();
    return mockEquipment.filter(
      item =>
        item.make.toLowerCase().includes(lowerQuery) ||
        item.model.toLowerCase().includes(lowerQuery) ||
        item.description?.toLowerCase().includes(lowerQuery)
    );
  },

  // Get statistics
  async getStats(): Promise<{
    total_equipment: number;
    tractors: number;
    combines: number;
    implements: number;
  }> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      total_equipment: mockEquipment.length,
      tractors: mockTractors.length,
      combines: mockCombines.length,
      implements: mockImplements.length,
    };
  },

  // Get error records
  async getErrorRecords(filters?: {
    category?: string;
    error_type?: string;
  }): Promise<ErrorRecord[]> {
    await new Promise(resolve => setTimeout(resolve, 300));
    let filtered = [...mockErrorRecords];

    if (filters?.category) {
      filtered = filtered.filter(err => err.category === filters.category);
    }

    if (filters?.error_type) {
      filtered = filtered.filter(err => err.error_type === filters.error_type);
    }

    return filtered;
  },

  // Delete error records by IDs
  async deleteErrorRecords(ids: string[]): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 300));
    // In a real implementation, this would make a DELETE request to the backend
    // For mock, we'll just simulate success
    console.log('Deleting error records:', ids);
  },
};
