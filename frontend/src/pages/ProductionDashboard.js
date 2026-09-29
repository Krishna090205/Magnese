import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import SourceTagBadge from '../components/SourceTagBadge';

const API_BASE = 'http://localhost:8000';

function ProductionDashboard() {
  const [shortfallPredictions, setShortfallPredictions] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedMine, setSelectedMine] = useState(null);
  const [selectedPrediction, setSelectedPrediction] = useState(null);
  const [explanations, setExplanations] = useState([]);
  const [productionData, setProductionData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch shortfall predictions
      const shortfallRes = await axios.get(`${API_BASE}/api/shortfall-forecast`);
      setShortfallPredictions(shortfallRes.data);
      
      // Fetch recommendations
      const recRes = await axios.get(`${API_BASE}/api/recommendations`);
      setRecommendations(recRes.data);
      
      setLoading(false);
      
    } catch (err) {
      console.error('Error fetching production data:', err);
      setError('Failed to load production data');
      setLoading(false);
    }
  };

  const handlePredictionClick = async (prediction) => {
    try {
      setSelectedPrediction(prediction);
      
      // Fetch explanations for this prediction
      const explRes = await axios.get(`${API_BASE}/api/explain/${prediction.id}`);
      setExplanations(explRes.data);
      
      // Fetch production data for this mine
      const prodRes = await axios.get(`${API_BASE}/api/mines/${prediction.mine_id}/production`);
      setProductionData(prodRes.data.slice(-30)); // Last 30 days
      
    } catch (err) {
      console.error('Error fetching prediction details:', err);
    }
  };

  const handleAction = async (recommendationId) => {
    try {
      await axios.post(`${API_BASE}/api/actions`, {
        recommendation_id: recommendationId,
        action_type: 'status_update',
        description: 'Marked as actioned from dashboard',
        performed_by: 'dashboard_user'
      });
      
      // Refresh recommendations
      const recRes = await axios.get(`${API_BASE}/api/recommendations`);
      setRecommendations(recRes.data);
      
    } catch (err) {
      console.error('Error marking action:', err);
      alert('Failed to mark action');
    }
  };

  const getRiskColor = (probability) => {
    if (probability >= 0.15) return '#ef4444'; // High risk - red
    if (probability >= 0.05) return '#f59e0b'; // Medium risk - orange
    return '#10b981'; // Low risk - green
  };

  const getRiskTier = (probability) => {
    if (probability >= 0.15) return 'High';
    if (probability >= 0.05) return 'Medium';
    return 'Low';
  };

  if (loading) {
    return <div className="loading">Loading production dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h2>Production & Shortfall Dashboard</h2>
        <SourceTagBadge sourceTag="SYNTHETIC" size="large" />
      </div>

      <div className="production-layout">
        {/* Shortfall Predictions List */}
        <div className="predictions-section">
          <h3>Shortfall Predictions (Next 7 Days)</h3>
          <div className="predictions-list">
            {shortfallPredictions.map(prediction => {
              const mineName = `Mine ${prediction.mine_id}`;
              return (
                <div 
                  key={prediction.id}
                  className={`prediction-item ${selectedPrediction?.id === prediction.id ? 'selected' : ''}`}
                  onClick={() => handlePredictionClick(prediction)}
                  style={{ borderLeft: `4px solid ${getRiskColor(prediction.probability)}` }}
                >
                  <div className="prediction-header">
                    <span className="prediction-mine">{mineName}</span>
                    <span className={`prediction-risk ${getRiskTier(prediction.probability).toLowerCase()}`}>
                      {getRiskTier(prediction.probability)} Risk
                    </span>
                  </div>
                  <div className="prediction-details">
                    <span>Target Date: {prediction.target_date}</span>
                    <span>Predicted Shortfall: {prediction.predicted_shortfall_tonnes?.toFixed(2)} tonnes</span>
                    <span>Risk: {(prediction.probability * 100).toFixed(1)}%</span>
                    <SourceTagBadge sourceTag={prediction.source_tag} />
                  </div>
                </div>
              );
            })}
          </div>
          <SourceTagBadge sourceTag="SYNTHETIC" />
        </div>

        {/* Charts and Details */}
        <div className="charts-section">
          {selectedPrediction ? (
            <>
              {/* Risk Gauge */}
              <div className="chart-card">
                <h3>Shortfall Risk Gauge</h3>
                <div className="risk-gauge">
                  <div 
                    className="risk-meter"
                    style={{ 
                      width: `${selectedPrediction.probability * 100}%`,
                      backgroundColor: getRiskColor(selectedPrediction.probability)
                    }}
                  />
                  <span className="risk-value">{(selectedPrediction.probability * 100).toFixed(1)}%</span>
                </div>
                <SourceTagBadge sourceTag={selectedPrediction.source_tag} />
              </div>

              {/* Contributing Factors Chart */}
              {explanations.length > 0 && (
                <div className="chart-card">
                  <h3>Contributing Factors</h3>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={explanations}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="feature_name" angle={-45} textAnchor="end" height={100} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="importance_score" fill="#3b82f6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <SourceTagBadge sourceTag="SYNTHETIC" />
                </div>
              )}

              {/* Production vs Plan Chart */}
              {productionData.length > 0 && (
                <div className="chart-card">
                  <h3>Production vs Plan (Last 30 Days)</h3>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height={250}>
                      <LineChart data={productionData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="record_date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="ore_extracted_tonnes" stroke="#10b981" name="Actual" />
                        <Line type="monotone" dataKey="target_tonnes" stroke="#3b82f6" name="Plan" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <SourceTagBadge sourceTag="SYNTHETIC" />
                </div>
              )}
            </>
          ) : (
            <div className="placeholder">
              <p>Select a prediction to view details</p>
            </div>
          )}
        </div>

        {/* Recommendations Panel */}
        <div className="recommendations-section">
          <h3>Recommended Actions</h3>
          <div className="recommendations-list">
            {recommendations
              .filter(rec => !selectedPrediction || rec.mine_id === selectedPrediction.mine_id)
              .slice(0, 10)
              .map(rec => (
                <div key={rec.id} className={`recommendation-item priority-${rec.priority}`}>
                  <div className="rec-header">
                    <span className="rec-type">{rec.recommendation_type}</span>
                    <span className={`rec-priority ${rec.priority}`}>{rec.priority}</span>
                  </div>
                  <div className="rec-title">{rec.title}</div>
                  <div className="rec-description">{rec.description}</div>
                  <button 
                    className="action-btn"
                    onClick={() => handleAction(rec.id)}
                    disabled={rec.status !== 'pending'}
                  >
                    {rec.status === 'pending' ? 'Mark as Actioned' : rec.status}
                  </button>
                  <SourceTagBadge sourceTag={rec.source_tag} />
                </div>
              ))}
          </div>
          <SourceTagBadge sourceTag="SYNTHETIC" />
        </div>
      </div>
    </div>
  );
}

export default ProductionDashboard;
