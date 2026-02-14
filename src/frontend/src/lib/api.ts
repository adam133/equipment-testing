// API client for OpenAg-DB backend
// This file provides functions to interact with the FastAPI backend

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
  grain_tank_capacity_bu?: number;
  separator_type?: string;
  engine_hp?: number;
}

export interface Implement extends Equipment {
  category: 'implement';
  working_width_ft?: number;
  weight_lbs?: number;
  required_hp_min?: number;
  required_hp_max?: number;
}

export interface Stats {
  total_equipment: number;
  tractors: number;
  combines: number;
  implements: number;
}

// Get API base URL from environment variable or use default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API client functions
export const api = {
  // Get all equipment
  async getAllEquipment(): Promise<Equipment[]> {
    const response = await fetch(`${API_BASE_URL}/equipment`);
    if (!response.ok) {
      throw new Error(`Failed to fetch equipment: ${response.statusText}`);
    }
    return response.json();
  },

  // Get equipment by category
  async getEquipmentByCategory(category: string): Promise<Equipment[]> {
    const response = await fetch(`${API_BASE_URL}/equipment?category=${encodeURIComponent(category)}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch equipment by category: ${response.statusText}`);
    }
    return response.json();
  },

  // Get tractors
  async getTractors(): Promise<Tractor[]> {
    const response = await fetch(`${API_BASE_URL}/equipment/tractors`);
    if (!response.ok) {
      throw new Error(`Failed to fetch tractors: ${response.statusText}`);
    }
    return response.json();
  },

  // Get combines
  async getCombines(): Promise<Combine[]> {
    const response = await fetch(`${API_BASE_URL}/equipment/combines`);
    if (!response.ok) {
      throw new Error(`Failed to fetch combines: ${response.statusText}`);
    }
    return response.json();
  },

  // Get implements
  async getImplements(): Promise<Implement[]> {
    const response = await fetch(`${API_BASE_URL}/equipment/implements`);
    if (!response.ok) {
      throw new Error(`Failed to fetch implements: ${response.statusText}`);
    }
    return response.json();
  },

  // Search equipment
  async searchEquipment(query: string): Promise<Equipment[]> {
    // For now, use the general equipment endpoint and filter on the backend later
    // This will need backend implementation for search functionality
    const allEquipment = await this.getAllEquipment();
    const lowerQuery = query.toLowerCase();
    return allEquipment.filter(
      item =>
        item.make.toLowerCase().includes(lowerQuery) ||
        item.model.toLowerCase().includes(lowerQuery) ||
        item.description?.toLowerCase().includes(lowerQuery)
    );
  },

  // Get statistics
  async getStats(): Promise<Stats> {
    const response = await fetch(`${API_BASE_URL}/stats`);
    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }
    return response.json();
  },
};
