import { useState, useEffect } from 'react';
import { mockApi, ErrorRecord } from '../lib/mockApi';
import './ErrorManagement.css';

export function ErrorManagement() {
  const [errors, setErrors] = useState<ErrorRecord[]>([]);
  const [filteredErrors, setFilteredErrors] = useState<ErrorRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [errorTypeFilter, setErrorTypeFilter] = useState<string>('all');
  const [deleting, setDeleting] = useState(false);

  // Get unique error types for filter
  const errorTypes = Array.from(new Set(errors.map(err => err.error_type)));

  useEffect(() => {
    loadErrors();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [categoryFilter, errorTypeFilter, errors]);

  const loadErrors = async () => {
    setLoading(true);
    try {
      const data = await mockApi.getErrorRecords();
      setErrors(data);
    } catch (error) {
      console.error('Failed to load error records:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = errors;

    if (categoryFilter !== 'all') {
      filtered = filtered.filter(err => err.category === categoryFilter);
    }

    if (errorTypeFilter !== 'all') {
      filtered = filtered.filter(err => err.error_type === errorTypeFilter);
    }

    setFilteredErrors(filtered);
  };

  const handleSelectAll = () => {
    if (selectedIds.size === filteredErrors.length) {
      // Deselect all
      setSelectedIds(new Set());
    } else {
      // Select all filtered errors
      setSelectedIds(new Set(filteredErrors.map(err => err.id)));
    }
  };

  const handleSelectOne = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const handleBatchDelete = async () => {
    if (selectedIds.size === 0) {
      alert('Please select at least one error record to delete.');
      return;
    }

    if (!confirm(`Are you sure you want to delete ${selectedIds.size} error record(s)?`)) {
      return;
    }

    setDeleting(true);
    try {
      await mockApi.deleteErrorRecords(Array.from(selectedIds));
      // Remove deleted errors from local state
      setErrors(errors.filter(err => !selectedIds.has(err.id)));
      setSelectedIds(new Set());
      alert(`Successfully deleted ${selectedIds.size} error record(s).`);
    } catch (error) {
      console.error('Failed to delete error records:', error);
      alert('Failed to delete error records. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteOne = async (id: string) => {
    if (!confirm('Are you sure you want to delete this error record?')) {
      return;
    }

    setDeleting(true);
    try {
      await mockApi.deleteErrorRecords([id]);
      // Remove deleted error from local state
      setErrors(errors.filter(err => err.id !== id));
      // Remove from selected if it was selected
      const newSelected = new Set(selectedIds);
      newSelected.delete(id);
      setSelectedIds(newSelected);
      alert('Successfully deleted 1 error record.');
    } catch (error) {
      console.error('Failed to delete error record:', error);
      alert('Failed to delete error record. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="error-management">
        <div className="loading">Loading error records...</div>
      </div>
    );
  }

  return (
    <div className="error-management">
      <header className="error-header">
        <h2>🔧 Error Records Management</h2>
        <p className="subtitle">View and manage error records from the scraping pipeline</p>
      </header>

      <section className="error-stats">
        <div className="stat">
          <span className="stat-value">{errors.length}</span>
          <span className="stat-label">Total Errors</span>
        </div>
        <div className="stat">
          <span className="stat-value">{filteredErrors.length}</span>
          <span className="stat-label">Filtered</span>
        </div>
        <div className="stat">
          <span className="stat-value">{selectedIds.size}</span>
          <span className="stat-label">Selected</span>
        </div>
      </section>

      <section className="error-controls">
        <div className="filters">
          <div className="filter-group">
            <label htmlFor="category-filter">Category:</label>
            <select
              id="category-filter"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Categories</option>
              <option value="tractor">Tractors</option>
              <option value="combine">Combines</option>
              <option value="implement">Implements</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="error-type-filter">Error Type:</label>
            <select
              id="error-type-filter"
              value={errorTypeFilter}
              onChange={(e) => setErrorTypeFilter(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Error Types</option>
              {errorTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="actions">
          <button
            onClick={handleSelectAll}
            className="btn btn-secondary"
            disabled={filteredErrors.length === 0}
          >
            {selectedIds.size === filteredErrors.length && filteredErrors.length > 0
              ? 'Deselect All'
              : 'Select All'}
          </button>
          <button
            onClick={handleBatchDelete}
            className="btn btn-danger"
            disabled={selectedIds.size === 0 || deleting}
          >
            {deleting ? 'Deleting...' : `Delete Selected (${selectedIds.size})`}
          </button>
        </div>
      </section>

      {filteredErrors.length === 0 ? (
        <div className="no-errors">
          <p>✅ No error records found matching the current filters.</p>
        </div>
      ) : (
        <section className="error-table-container">
          <table className="error-table">
            <thead>
              <tr>
                <th className="checkbox-col">
                  <input
                    type="checkbox"
                    checked={selectedIds.size === filteredErrors.length && filteredErrors.length > 0}
                    onChange={handleSelectAll}
                    aria-label="Select all"
                  />
                </th>
                <th>Category</th>
                <th>Error Type</th>
                <th>Make</th>
                <th>Model</th>
                <th>Error Message</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredErrors.map((error) => (
                <tr key={error.id} className={selectedIds.has(error.id) ? 'selected' : ''}>
                  <td className="checkbox-col">
                    <input
                      type="checkbox"
                      checked={selectedIds.has(error.id)}
                      onChange={() => handleSelectOne(error.id)}
                      aria-label={`Select ${error.id}`}
                    />
                  </td>
                  <td>
                    <span className={`category-badge category-${error.category}`}>
                      {error.category}
                    </span>
                  </td>
                  <td>
                    <span className="error-type-badge">{error.error_type}</span>
                  </td>
                  <td>{error.make || '—'}</td>
                  <td>{error.model || '—'}</td>
                  <td className="error-message">{error.error_message}</td>
                  <td>
                    <button
                      onClick={() => handleDeleteOne(error.id)}
                      className="btn-icon"
                      title="Delete this record"
                      disabled={deleting}
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
