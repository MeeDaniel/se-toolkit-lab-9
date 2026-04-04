import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts';
import './StatisticsDashboard.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4ade80', '#fbbf24', '#f87171'];

function StatisticsDashboard() {
  const [statistics, setStatistics] = useState(null);
  const [correlations, setCorrelations] = useState(null);
  const [excursions, setExcursions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsRes, corrRes, excRes] = await Promise.all([
        axios.get(`${API_URL}/api/statistics/`),
        axios.get(`${API_URL}/api/statistics/correlations`),
        axios.get(`${API_URL}/api/excursions/?limit=10`),
      ]);

      setStatistics(statsRes.data);
      setCorrelations(corrRes.data);
      setExcursions(excRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
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

      {correlations && correlations.correlations && (
        <div className="correlations-section">
          <h3>Correlation Analysis</h3>
          <div className="correlation-cards">
            {Object.entries(correlations.correlations).map(([key, value]) => (
              <div key={key} className="correlation-card">
                <div className="correlation-header">
                  <h4>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                  <div className={`correlation-value ${Math.abs(value) > 0.4 ? 'strong' : 'weak'}`}>
                    {value.toFixed(2)}
                  </div>
                </div>
                <p className="correlation-insight">
                  {Math.abs(value) > 0.7 ? 'Strong' : Math.abs(value) > 0.4 ? 'Moderate' : 'Weak'}{' '}
                  {value > 0 ? 'positive' : 'negative'} correlation
                </p>
              </div>
            ))}
          </div>
          {correlations.insights && (
            <div className="insights-box">
              <h4>Insights</h4>
              <p>{correlations.insights}</p>
            </div>
          )}
        </div>
      )}

      <div className="recent-excursions">
        <h3>Recent Excursions</h3>
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
            </tr>
          </thead>
          <tbody>
            {excursions.slice(0, 10).map(exc => (
              <tr key={exc.id}>
                <td>{exc.id}</td>
                <td>{exc.number_of_tourists}</td>
                <td>{exc.average_age.toFixed(1)}</td>
                <td>{(exc.vivacity_before * 100).toFixed(0)}%</td>
                <td>{(exc.vivacity_after * 100).toFixed(0)}%</td>
                <td>{(exc.interest_in_it * 100).toFixed(0)}%</td>
                <td className="interests-cell">{exc.interests_list}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default StatisticsDashboard;
