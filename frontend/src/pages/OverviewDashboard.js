import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import SourceTagBadge from '../components/SourceTagBadge';

const API_BASE = 'http://localhost:8000';

function OverviewDashboard() {
  const [overview, setOverview] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [productionData, setProductionData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch overview data
      const overviewRes = await axios.get(`${API_BASE}/api/overview`);
      setOverview(overviewRes.data);
      
      // Fetch alerts
      const alertsRes = await axios.get(`${API_BASE}/api/alerts?limit=10`);
      setAlerts(alertsRes.data.alerts);
      
      // Fetch production data for trend chart
      const minesRes = await axios.get(`${API_BASE}/api/mines`);
      const mines = minesRes.data;
      
      // Get production data for each mine
      const productionPromises = mines.slice(0, 5).map(async (mine) => {
        try {
          const prodRes = await axios.get(`${API_BASE}/api/mines/${mine.id}/production`);
          return {
            name: mine.name,
            data: prodRes.data.slice(-30) // Last 30 days
          };
        } catch (e) {
          return { name: mine.name, data: [] };
        }
      });
      
      const productionResults = await Promise.all(productionPromises);
      
      // Format for chart
      const chartData = productionResults.flatMap(mine => 
        mine.data.map(record => ({
          date: record.record_date,
          mine: mine.name,
          production: record.ore_extracted_tonnes || 0,
          shortfall: record.shortfall_tonnes || 0
        }))
      );
      
      setProductionData(chartData);
      setLoading(false);
      
    } catch (err) {
      console.error('Error fetching overview data:', err);
      setError('Failed to load dashboard data');
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h2>Overview Dashboard</h2>
        <SourceTagBadge sourceTag={overview?.source_tag_provenance ? 'SYNTHETIC' : 'SYNTHETIC'} size="large" />
      </div>

      {/* Portfolio Cards */}
      <div className="portfolio-cards">
        <div className="card" onClick={() => window.location.href = '/production'}>
          <h3>Mines Monitored</h3>
          <div className="card-value">{overview?.mines_monitored || 0}</div>
          <div className="card-label">Active mines in system</div>
          <SourceTagBadge sourceTag="REAL_PUBLIC" />
        </div>

        <div className="card alert-card" onClick={() => window.location.href = '/production'}>
          <h3>Active Shortfall Alerts</h3>
          <div className="card-value alert">{overview?.active_shortfall_alerts || 0}</div>
          <div className="card-label">Predictions ≥5% risk</div>
          <SourceTagBadge sourceTag="SYNTHETIC" />
        </div>

        <div className="card target-card" onClick={() => window.location.href = '/exploration'}>
          <h3>Exploration Targets</h3>
          <div className="card-value target">{overview?.active_exploration_targets || 0}</div>
          <div className="card-label">High-confidence reserve predictions</div>
          <SourceTagBadge sourceTag="SYNTHETIC" />
        </div>

        <div className="card">
          <h3>Data Freshness</h3>
          <div className="card-value">
            {overview?.data_freshness?.latest_shortfall_prediction 
              ? new Date(overview.data_freshness.latest_shortfall_prediction).toLocaleDateString()
              : 'N/A'}
          </div>
          <div className="card-label">Latest prediction date</div>
          <SourceTagBadge sourceTag="SYNTHETIC" />
        </div>
      </div>

      {/* Production vs Plan Trend Chart */}
      <div className="chart-section">
        <h3>Production vs Plan Trend (Last 30 Days)</h3>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={productionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="production" stroke="#3b82f6" name="Actual Production" />
              <Line type="monotone" dataKey="shortfall" stroke="#ef4444" name="Shortfall" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <SourceTagBadge sourceTag="SYNTHETIC" />
      </div>

      {/* Alert List */}
      <div className="alerts-section">
        <h3>Recent Alerts</h3>
        <div className="alerts-list">
          {alerts.length === 0 ? (
            <p className="no-alerts">No active alerts</p>
          ) : (
            alerts.map((alert) => (
              <div 
                key={alert.id} 
                className={`alert-item ${alert.severity}`}
                onClick={() => alert.type === 'shortfall' 
                  ? (window.location.href = '/production') 
                  : (window.location.href = '/exploration')
                }
              >
                <div className="alert-header">
                  <span className="alert-type">{alert.type.toUpperCase()}</span>
                  <span className={`alert-severity ${alert.severity}`}>{alert.severity}</span>
                </div>
                <div className="alert-mine">{alert.mine_name}</div>
                <div className="alert-details">
                  {alert.type === 'shortfall' ? (
                    <>
                      <span>Predicted Shortfall: {alert.predicted_shortfall_tonnes?.toFixed(2)} tonnes</span>
                      <span>Risk: {(alert.probability * 100).toFixed(1)}%</span>
                    </>
                  ) : (
                    <>
                      <span>Predicted Reserve: {alert.predicted_reserve_tonnes?.toFixed(2)} tonnes</span>
                      <span>Confidence: {(alert.confidence_level * 100).toFixed(0)}%</span>
                    </>
                  )}
                </div>
                <SourceTagBadge sourceTag={alert.source_tag} />
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default OverviewDashboard;
