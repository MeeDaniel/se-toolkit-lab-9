import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from 'recharts';
import './StatisticsDashboard.css';

const API_URL = process.env.REACT_APP_API_URL || '';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4ade80', '#fbbf24', '#f87171'];

function StatisticsDashboard({ user, refreshTrigger }) {
  const [statistics, setStatistics] = useState(null);
  const [correlations, setCorrelations] = useState(null);
  const [excursions, setExcursions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [editingExcursion, setEditingExcursion] = useState(null);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    if (user && user.id && refreshTrigger) {
      setOffset(0);
      fetchData(user.id, 0);
    }
  }, [user, refreshTrigger]);

  const fetchData = async (userId, currentOffset, isLoadMore = false) => {
    try {
      // Only show full loading state on initial load
      if (!isLoadMore) {
        setLoading(true);
      }
      
      const [statsRes, corrRes, excRes] = await Promise.all([
        axios.get(`${API_URL}/statistics/?user_id=${userId}`),
        axios.get(`${API_URL}/statistics/correlations?user_id=${userId}`),
        axios.get(`${API_URL}/excursions/?user_id=${userId}&limit=10&offset=${currentOffset}`),
      ]);

      setStatistics(statsRes.data);
      setCorrelations(corrRes.data);
      
      // If loading more, append to existing data
      if (isLoadMore) {
        setExcursions(prev => [...prev, ...excRes.data]);
      } else {
        setExcursions(excRes.data);
      }
      
      // Check if there are more excursions to load
      if (excRes.data.length < 10) {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMore = () => {
    const newOffset = offset + 10;
    setOffset(newOffset);
    if (user && user.id) {
      fetchData(user.id, newOffset, true);
    }
  };

  const openEditModal = (excursion) => {
    setEditingExcursion(excursion);
    setEditForm({
      number_of_tourists: excursion.number_of_tourists,
      average_age: excursion.average_age,
      age_distribution: excursion.age_distribution,
      vivacity_before: excursion.vivacity_before,
      vivacity_after: excursion.vivacity_after,
      interest_in_it: excursion.interest_in_it,
      interests_list: excursion.interests_list
    });
  };

  const closeEditModal = () => {
    setEditingExcursion(null);
    setEditForm({});
  };

  const saveEdit = async () => {
    try {
      await axios.put(
        `${API_URL}/excursions/${editingExcursion.id}`,
        editForm,
        { params: { user_id: user.id } }
      );
      // Refresh data after save
      fetchData(user.id, 0);
      closeEditModal();
    } catch (error) {
      console.error('Error saving excursion:', error);
      alert('Failed to save changes');
    }
  };

  const deleteExcursion = async (excursionId) => {
    if (!window.confirm('Are you sure you want to delete this excursion? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(
        `${API_URL}/excursions/${excursionId}`,
        { params: { user_id: user.id } }
      );
      // Refresh data after delete
      fetchData(user.id, 0);
    } catch (error) {
      console.error('Error deleting excursion:', error);
      alert('Failed to delete excursion');
    }
  };

  if (loading && excursions.length === 0) {
    return <div className="loading">Loading statistics...</div>;
  }

  if (!statistics || statistics.total_excursions === 0) {
    return (
      <div className="no-data">
        <h2>No Data Yet</h2>
        <p>Start chatting with the AI assistant to add excursion data.</p>
      </div>
    );
  }

  const interestData = statistics.top_interests.slice(0, 6).map((interest, idx) => ({
    name: interest,
    value: Math.floor(Math.random() * 10) + 1, // Placeholder - would be real count
  }));

  const vivacityData = [
    { name: 'Before', value: statistics.avg_vivacity_before },
    { name: 'After', value: statistics.avg_vivacity_after },
  ];

  // Extract summary data from correlations if available
  const corrSummary = correlations?.summary;
  const topCorrelations = correlations?.summary?.most_interesting_correlations || [];
  const allCorrelations = correlations?.all_correlations || [];

  return (
    <div className="statistics-dashboard">
      <div className="dashboard-header">
        <h2>Statistics Dashboard</h2>
        <button onClick={fetchData} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{statistics.total_excursions}</div>
          <div className="stat-label">Total Excursions</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{statistics.avg_tourists_per_excursion.toFixed(1)}</div>
          <div className="stat-label">Avg Tourists/Excursion</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{statistics.avg_age_all.toFixed(1)}</div>
          <div className="stat-label">Average Age</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{(statistics.avg_interest_in_it * 100).toFixed(0)}%</div>
          <div className="stat-label">IT Interest</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Vivacity: Before vs After</h3>
          <BarChart width={400} height={300} data={vivacityData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 1]} />
            <Tooltip />
            <Bar dataKey="value" fill="#667eea" />
          </BarChart>
        </div>

        <div className="chart-card">
          <h3>Top Tourist Interests</h3>
          <PieChart width={400} height={300}>
            <Pie
              data={interestData}
              cx={200}
              cy={150}
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {interestData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </div>
      </div>

      {corrSummary && (
        <div className="correlations-section">
          <h3>📊 Key Insights</h3>
          
          {/* Summary cards */}
          <div className="insights-summary">
            <div className="insight-card">
              <div className="insight-icon">👥</div>
              <div className="insight-value">{corrSummary.avg_group_size}</div>
              <div className="insight-label">Avg Tourists/Tour</div>
            </div>
            <div className="insight-card">
              <div className="insight-icon">{corrSummary.avg_vivacity_boost > 0.1 ? '🔥' : '📊'}</div>
              <div className="insight-value">+{(corrSummary.avg_vivacity_boost * 100).toFixed(0)}%</div>
              <div className="insight-label">Avg Energy Boost</div>
            </div>
            {corrSummary.best_excursion && (
              <div className="insight-card">
                <div className="insight-icon">🏆</div>
                <div className="insight-value">#{corrSummary.best_excursion.id}</div>
                <div className="insight-label">Best Tour (+{(corrSummary.best_excursion.vivacity_boost * 100).toFixed(0)}%)</div>
              </div>
            )}
          </div>

          {/* Top correlations */}
          <div className="top-correlations">
            <h4>🔍 Top Correlations Found</h4>
            {topCorrelations.length > 0 ? (
              <div className="correlation-list">
                {topCorrelations.map((corr, idx) => (
                  <div key={corr.id} className={`correlation-item ${corr.type}`}>
                    <div className="correlation-item-header">
                      <span className="correlation-rank">#{idx + 1}</span>
                      <span className={`correlation-strength ${corr.strength}`}>
                        {corr.strength} {corr.direction}
                      </span>
                    </div>
                    <div className="correlation-item-label">{corr.label}</div>
                    <div className="correlation-item-value">
                      {corr.type === 'correlation' ? `r = ${corr.value.toFixed(2)}` : corr.formatted_value}
                    </div>
                    <div className="correlation-item-interpretation">{corr.interpretation}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-correlations">Add more excursions (at least 3) to see meaningful correlations.</p>
            )}
          </div>

          {/* All correlations toggle */}
          {allCorrelations.length > 5 && (
            <details className="all-correlations">
              <summary>📈 View All {allCorrelations.length} Correlations</summary>
              <div className="correlation-list">
                {allCorrelations.map((corr) => (
                  <div key={corr.id} className={`correlation-item ${corr.type}`}>
                    <div className="correlation-item-header">
                      <span className="correlation-label">{corr.label}</span>
                      <span className={`correlation-strength ${corr.strength || 'average'}`}>
                        {corr.type === 'correlation' ? `r = ${corr.value.toFixed(2)}` : corr.formatted_value}
                      </span>
                    </div>
                    <div className="correlation-item-interpretation">{corr.interpretation}</div>
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}

      <div className="recent-excursions">
        <h3>Recent Excursions ({excursions.length})</h3>
        {excursions.length === 0 ? (
          <p className="no-excursions">No excursions yet. Start chatting to add your first excursion!</p>
        ) : (
          <>
            <table className="excursions-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Tourists</th>
                  <th>Avg Age</th>
                  <th>Vivacity Before</th>
                  <th>Vivacity After</th>
                  <th>IT Interest</th>
                  <th>Interests</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {excursions.map(exc => (
                  <tr key={exc.id}>
                    <td>{exc.id}</td>
                    <td>{exc.number_of_tourists}</td>
                    <td>{exc.average_age.toFixed(1)}</td>
                    <td>{(exc.vivacity_before * 100).toFixed(0)}%</td>
                    <td>{(exc.vivacity_after * 100).toFixed(0)}%</td>
                    <td>{(exc.interest_in_it * 100).toFixed(0)}%</td>
                    <td className="interests-cell">{exc.interests_list}</td>
                    <td>
                      <div className="action-buttons">
                        <button className="edit-btn" onClick={() => openEditModal(exc)}>✏️ Edit</button>
                        <button className="delete-btn" onClick={() => deleteExcursion(exc.id)}>🗑️ Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {hasMore && (
              <div className="load-more-container">
                <button className="load-more-btn" onClick={loadMore} disabled={loading}>
                  {loading ? 'Loading...' : '📥 Load 10 More Excursions'}
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Edit Modal */}
      {editingExcursion && (
        <div className="modal-overlay" onClick={closeEditModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>✏️ Edit Excursion #{editingExcursion.id}</h3>
              <button className="close-btn" onClick={closeEditModal}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-grid">
                <div className="form-group">
                  <label>Number of Tourists</label>
                  <input
                    type="number"
                    value={editForm.number_of_tourists || ''}
                    onChange={e => setEditForm({...editForm, number_of_tourists: parseInt(e.target.value) || 0})}
                  />
                </div>
                <div className="form-group">
                  <label>Average Age</label>
                  <input
                    type="number"
                    step="0.1"
                    value={editForm.average_age || ''}
                    onChange={e => setEditForm({...editForm, average_age: parseFloat(e.target.value) || 0})}
                  />
                </div>
                <div className="form-group">
                  <label>Vivacity Before (0-100%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={(editForm.vivacity_before || 0) * 100}
                    onChange={e => setEditForm({...editForm, vivacity_before: parseFloat(e.target.value) / 100})}
                  />
                </div>
                <div className="form-group">
                  <label>Vivacity After (0-100%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={(editForm.vivacity_after || 0) * 100}
                    onChange={e => setEditForm({...editForm, vivacity_after: parseFloat(e.target.value) / 100})}
                  />
                </div>
                <div className="form-group">
                  <label>IT Interest (0-100%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={(editForm.interest_in_it || 0) * 100}
                    onChange={e => setEditForm({...editForm, interest_in_it: parseFloat(e.target.value) / 100})}
                  />
                </div>
                <div className="form-group full-width">
                  <label>Interests (space-separated keywords)</label>
                  <input
                    type="text"
                    value={editForm.interests_list || ''}
                    onChange={e => setEditForm({...editForm, interests_list: e.target.value})}
                  />
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="cancel-btn" onClick={closeEditModal}>Cancel</button>
              <button className="save-btn" onClick={saveEdit}>💾 Save Changes</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default StatisticsDashboard;
