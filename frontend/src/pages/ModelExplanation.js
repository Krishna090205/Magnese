import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import SourceTagBadge from '../components/SourceTagBadge';

const API_BASE = 'http://localhost:8000';

function ModelExplanation() {
  const [predictionId, setPredictionId] = useState('');
  const [predictionType, setPredictionType] = useState('shortfall');
  const [explanations, setExplanations] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [dataQuality, setDataQuality] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!predictionId) {
      setError('Please enter a prediction ID');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Fetch explanations
      const explRes = await axios.get(`${API_BASE}/api/explain/${predictionId}`);
      setExplanations(explRes.data);
      
      // Fetch prediction details
      if (predictionType === 'shortfall') {
        const predRes = await axios.get(`${API_BASE}/api/shortfall-forecast`);
        const pred = predRes.data.find(p => p.id === parseInt(predictionId));
        setPrediction(pred);
      } else {
        const predRes = await axios.get(`${API_BASE}/api/reserve-targets`);
        const pred = predRes.data.find(p => p.id === parseInt(predictionId));
        setPrediction(pred);
      }
      
      // Fetch data quality
      const dqRes = await axios.get(`${API_BASE}/api/data-quality?limit=20`);
      setDataQuality(dqRes.data);
      
      setLoading(false);
      
    } catch (err) {
      console.error('Error fetching explanation:', err);
      setError('Failed to load explanation. Check prediction ID and try again.');
      setLoading(false);
    }
  };

  const getSourceTagColor = (tag) => {
    const colors = {
      'REAL_OFFICIAL': '#10b981',
      'REAL_PUBLIC': '#3b82f6',
      'PROXY': '#f59e0b',
      'SYNTHETIC': '#ef4444'
    };
    return colors[tag] || '#6b7280';
  };

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h2>Model Explanation & Data Quality</h2>
        <SourceTagBadge sourceTag="SYNTHETIC" size="large" />
      </div>

      {/* Search Section */}
      <div className="search-section">
        <div className="search-controls">
          <div className="search-input">
            <label>Prediction ID:</label>
            <input
              type="number"
              value={predictionId}
              onChange={(e) => setPredictionId(e.target.value)}
              placeholder="Enter prediction ID"
            />
          </div>
          <div className="search-select">
            <label>Prediction Type:</label>
            <select value={predictionType} onChange={(e) => setPredictionType(e.target.value)}>
              <option value="shortfall">Shortfall Prediction</option>
              <option value="reserve">Reserve Prediction</option>
            </select>
          </div>
          <button className="search-btn" onClick={handleSearch}>
            Get Explanation
          </button>
        </div>
        <SourceTagBadge sourceTag="SYNTHETIC" />
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      {loading && (
        <div className="loading">Loading explanation...</div>
      )}

      {explanations.length > 0 && !loading && (
        <div className="explanation-results">
          {/* Prediction Summary */}
          {prediction && (
            <div className="prediction-summary">
              <h3>Prediction Summary</h3>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="label">Prediction ID:</span>
                  <span className="value">{prediction.id}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Type:</span>
                  <span className="value">{predictionType}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Mine ID:</span>
                  <span className="value">{prediction.mine_id}</span>
                </div>
                {predictionType === 'shortfall' ? (
                  <>
                    <div className="summary-item">
                      <span className="label">Predicted Shortfall:</span>
                      <span className="value">{prediction.predicted_shortfall_tonnes?.toFixed(2)} tonnes</span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Probability:</span>
                      <span className="value">{(prediction.probability * 100).toFixed(1)}%</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="summary-item">
                      <span className="label">Predicted Reserve:</span>
                      <span className="value">{prediction.predicted_reserve_tonnes?.toFixed(2)} tonnes</span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Confidence:</span>
                      <span className="value">{(prediction.confidence_level * 100).toFixed(0)}%</span>
                    </div>
                  </>
                )}
                <div className="summary-item">
                  <span className="label">Model Version:</span>
                  <span className="value">{prediction.model_version}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Source Tag:</span>
                  <SourceTagBadge sourceTag={prediction.source_tag} />
                </div>
              </div>
            </div>
          )}

          {/* Feature Contributions Chart */}
          <div className="feature-contributions">
            <h3>Feature Contributions</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={explanations}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="feature_name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="importance_score" fill="#3b82f6" name="Importance Score" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <SourceTagBadge sourceTag="SYNTHETIC" />
          </div>

          {/* Feature Details Table */}
          <div className="feature-details">
            <h3>Feature Details</h3>
            <table className="feature-table">
              <thead>
                <tr>
                  <th>Feature Name</th>
                  <th>Feature Value</th>
                  <th>Importance Score</th>
                  <th>Direction</th>
                  <th>Source Tag</th>
                </tr>
              </thead>
              <tbody>
                {explanations.map(expl => (
                  <tr key={expl.id}>
                    <td>{expl.feature_name}</td>
                    <td>{expl.feature_value?.toFixed(4)}</td>
                    <td>{(expl.importance_score * 100).toFixed(1)}%</td>
                    <td>{expl.direction}</td>
                    <td><SourceTagBadge sourceTag={expl.source_tag} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
            <SourceTagBadge sourceTag="SYNTHETIC" />
          </div>

          {/* Data Quality Panel */}
          <div className="data-quality-panel">
            <h3>Data Quality Status</h3>
            <div className="quality-list">
              {dataQuality.length > 0 ? (
                dataQuality.map(dq => (
                  <div key={dq.id} className={`quality-item status-${dq.status}`}>
                    <div className="quality-header">
                      <span className="quality-table">{dq.table_name}</span>
                      <span className={`quality-status ${dq.status}`}>{dq.status}</span>
                    </div>
                    <div className="quality-details">
                      <span className="quality-type">{dq.check_type}</span>
                      <span className="quality-desc">{dq.check_description}</span>
                    </div>
                    {dq.error_message && (
                      <div className="quality-error">{dq.error_message}</div>
                    )}
                    <SourceTagBadge sourceTag={dq.source_tag} />
                  </div>
                ))
              ) : (
                <p className="no-quality-data">No data quality records found</p>
              )}
            </div>
            <SourceTagBadge sourceTag="SYNTHETIC" />
          </div>

          {/* Data Source Provenance */}
          <div className="data-provenance">
            <h3>Data Source Provenance</h3>
            <div className="provenance-info">
              <p><strong>Training Data Sources:</strong></p>
              <ul>
                <li>Drillhole & Assay Data: <SourceTagBadge sourceTag="SYNTHETIC" /> (synthetic for prototype)</li>
                <li>Production Data: <SourceTagBadge sourceTag="SYNTHETIC" /> (synthetic for prototype)</li>
                <li>Environmental Data: <SourceTagBadge sourceTag="SYNTHETIC" /> (synthetic for prototype)</li>
                <li>Mine Locations: <SourceTagBadge sourceTag="REAL_PUBLIC" /> (from MOIL public reports)</li>
              </ul>
              <p><strong>Model Type:</strong> {predictionType === 'shortfall' ? 'Gradient-Boosted Regressor (XGBoost)' : 'Gradient-Boosted Classifier (XGBoost)'}</p>
              <p><strong>Training Samples:</strong> {predictionType === 'shortfall' ? '4,032' : '632'}</p>
              <p><strong>Known Limitations:</strong> Model trained on synthetic data; real performance on MOIL data unknown. Retraining with actual MOIL data required for production use.</p>
            </div>
            <SourceTagBadge sourceTag="SYNTHETIC" />
          </div>
        </div>
      )}
    </div>
  );
}

export default ModelExplanation;
