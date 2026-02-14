import { useState, useEffect } from 'react';
import { api, Equipment } from './lib/api';
import { EquipmentCard } from './components/EquipmentCard';
import { ErrorManagement } from './components/ErrorManagement';
import './App.css';

type View = 'equipment' | 'errors';

function App() {
  const [currentView, setCurrentView] = useState<View>('equipment');
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [filteredEquipment, setFilteredEquipment] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState({
    total_equipment: 0,
    tractors: 0,
    combines: 0,
    implements: 0,
  });

  useEffect(() => {
    // Load equipment data
    const loadData = async () => {
      setLoading(true);
      try {
        const [equipmentData, statsData] = await Promise.all([
          api.getAllEquipment(),
          api.getStats(),
        ]);
        setEquipment(equipmentData);
        setFilteredEquipment(equipmentData);
        setStats(statsData);
      } catch (error) {
        console.error('Failed to load equipment data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  useEffect(() => {
    // Filter equipment based on category and search query
    let filtered = equipment;

    if (categoryFilter !== 'all') {
      filtered = filtered.filter(item => item.category === categoryFilter);
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        item =>
          item.make.toLowerCase().includes(query) ||
          item.model.toLowerCase().includes(query) ||
          item.description?.toLowerCase().includes(query)
      );
    }

    setFilteredEquipment(filtered);
  }, [categoryFilter, searchQuery, equipment]);

  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1>🌾 OpenAg-DB</h1>
          <p className="tagline">Open Agricultural Equipment Database</p>
          <nav className="nav-tabs">
            <button
              className={`nav-tab ${currentView === 'equipment' ? 'active' : ''}`}
              onClick={() => setCurrentView('equipment')}
            >
              Equipment
            </button>
            <button
              className={`nav-tab ${currentView === 'errors' ? 'active' : ''}`}
              onClick={() => setCurrentView('errors')}
            >
              Error Records
            </button>
          </nav>
        </div>
      </header>

      <main className="container">
        {currentView === 'equipment' ? (
          <>
            <section className="stats">
              <div className="stat-card">
                <div className="stat-value">{stats.total_equipment}</div>
                <div className="stat-label">Total Equipment</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.tractors}</div>
                <div className="stat-label">Tractors</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.combines}</div>
                <div className="stat-label">Combines</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.implements}</div>
                <div className="stat-label">Implements</div>
              </div>
            </section>

            <section className="filters">
              <div className="search-box">
                <input
                  type="text"
                  placeholder="Search equipment..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input"
                />
              </div>

              <div className="category-filters">
                <button
                  className={`filter-btn ${categoryFilter === 'all' ? 'active' : ''}`}
                  onClick={() => setCategoryFilter('all')}
                >
                  All
                </button>
                <button
                  className={`filter-btn ${categoryFilter === 'tractor' ? 'active' : ''}`}
                  onClick={() => setCategoryFilter('tractor')}
                >
                  Tractors
                </button>
                <button
                  className={`filter-btn ${categoryFilter === 'combine' ? 'active' : ''}`}
                  onClick={() => setCategoryFilter('combine')}
                >
                  Combines
                </button>
                <button
                  className={`filter-btn ${categoryFilter === 'implement' ? 'active' : ''}`}
                  onClick={() => setCategoryFilter('implement')}
                >
                  Implements
                </button>
              </div>
            </section>

            {loading ? (
              <div className="loading">Loading equipment data...</div>
            ) : (
              <>
                <section className="results-info">
                  <p>
                    Showing {filteredEquipment.length} of {equipment.length} equipment
                  </p>
                </section>

                <section className="equipment-grid">
                  {filteredEquipment.length === 0 ? (
                    <div className="no-results">
                      <p>No equipment found matching your criteria.</p>
                    </div>
                  ) : (
                    filteredEquipment.map((item) => (
                      <EquipmentCard
                        key={`${item.category}-${item.make}-${item.model}-${item.year_start || 'unknown'}`}
                        equipment={item}
                      />
                    ))
                  )}
                </section>
              </>
            )}
          </>
        ) : (
          <ErrorManagement />
        )}
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>
            OpenAg-DB - Community-driven agricultural equipment database
          </p>
          <p className="note">
            Connected to Unity Catalog backend for real-time equipment data.
          </p>
          <p>
            <a
              href="https://github.com/adam133/equipment-testing"
              target="_blank"
              rel="noopener noreferrer"
            >
              View on GitHub
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
