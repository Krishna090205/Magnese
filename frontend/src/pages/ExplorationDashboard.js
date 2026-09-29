import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import axios from 'axios';
import SourceTagBadge from '../components/SourceTagBadge';

const API_BASE = 'http://localhost:8000';

function ExplorationDashboard() {
  const [mines, setMines] = useState([]);
  const [reservePredictions, setReservePredictions] = useState([]);
  const [drillholes, setDrillholes] = useState([]);
  const [selectedLayer, setSelectedLayer] = useState('reserve');
  const [selectedPrediction, setSelectedPrediction] = useState(null);
  const [explanations, setExplanations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch mines
      const minesRes = await axios.get(`${API_BASE}/api/mines`);
      setMines(minesRes.data);
      
      // Fetch reserve predictions
      const reserveRes = await axios.get(`${API_BASE}/api/reserve-targets`);
      setReservePredictions(reserveRes.data);
      
      // Fetch drillholes for all mines
      const drillholePromises = minesRes.data.map(async (mine) => {
        try {
          const dhRes = await axios.get(`${API_BASE}/api/mines/${mine.id}/drillholes`);
          return dhRes.data.map(dh => ({ ...dh, mine_name: mine.name }));
        } catch (e) {
          return [];
        }
      });
      
      const drillholeResults = await Promise.all(drillholePromises);
      setDrillholes(drillholeResults.flat());
      
      setLoading(false);
      
    } catch (err) {
      console.error('Error fetching exploration data:', err);
      setError('Failed to load exploration data');
      setLoading(false);
    }
  };

  const handlePredictionClick = async (prediction) => {
    try {
      setSelectedPrediction(prediction);
      
      // Fetch explanations for this prediction
      const explRes = await axios.get(`${API_BASE}/api/explain/${prediction.id}`);
      setExplanations(explRes.data);
      
    } catch (err) {
      console.error('Error fetching explanations:', err);
    }
  };

  const getLayerColor = (layer) => {
    const colors = {
      'reserve': '#10b981',
      'drillholes': '#8b5cf6',
      'ndvi': '#22c55e',
      'soil_moisture': '#3b82f6',
      'lst': '#f59e0b',
      'rainfall': '#6366f1'
    };
    return colors[layer] || '#10b981';
  };

  const getGradeColor = (grade) => {
    if (grade >= 30) return '#ef4444'; // High grade - red
    if (grade >= 20) return '#f59e0b'; // Medium grade - orange
    return '#10b981'; // Low grade - green
  };

  if (loading) {
    return <div className="loading">Loading exploration dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h2>Exploration & Reserve Targeting</h2>
        <SourceTagBadge sourceTag="SYNTHETIC" size="large" />
      </div>

      <div className="exploration-layout">
        {/* Map Section */}
        <div className="map-section">
          <div className="layer-controls">
            <h4>Map Layers</h4>
            <div className="layer-buttons">
              {['reserve', 'drillholes', 'ndvi', 'soil_moisture', 'lst', 'rainfall'].map(layer => (
                <button
                  key={layer}
                  className={`layer-btn ${selectedLayer === layer ? 'active' : ''}`}
                  onClick={() => setSelectedLayer(layer)}
                  style={{ borderColor: getLayerColor(layer) }}
                >
                  {layer.replace('_', ' ').toUpperCase()}
                </button>
              ))}
            </div>
            <SourceTagBadge sourceTag="SYNTHETIC" />
          </div>

          <MapContainer center={[21.5, 79.5]} zoom={8} style={{ height: '500px', width: '100%' }}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; OpenStreetMap contributors'
            />
            
            {/* Mine locations */}
            {mines.map(mine => (
              <Marker 
                key={mine.id} 
                position={[21.0 + (mine.id * 0.1), 79.0 + (mine.id * 0.1)]}
              >
                <Popup>
                  <div>
                    <strong>{mine.name}</strong>
                    <p>State: {mine.state}</p>
                    <p>Status: {mine.operational_status}</p>
                    <SourceTagBadge sourceTag={mine.source_tag} />
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Reserve predictions as heatmap (circles) */}
            {selectedLayer === 'reserve' && reservePredictions.map(prediction => (
              <CircleMarker
                key={prediction.id}
                center={[21.0 + (prediction.mine_id * 0.1) + (Math.random() * 0.05), 79.0 + (prediction.mine_id * 0.1) + (Math.random() * 0.05)]}
                radius={10 + (prediction.predicted_reserve_tonnes / 1000)}
                color={getGradeColor(prediction.predicted_reserve_tonnes / 100)}
                fillColor={getGradeColor(prediction.predicted_reserve_tonnes / 100)}
                fillOpacity={0.5}
                onClick={() => handlePredictionClick(prediction)}
              >
                <Popup>
                  <div>
                    <strong>Reserve Prediction</strong>
                    <p>Predicted: {prediction.predicted_reserve_tonnes?.toFixed(2)} tonnes</p>
                    <p>Confidence: {(prediction.confidence_level * 100).toFixed(0)}%</p>
                    <SourceTagBadge sourceTag={prediction.source_tag} />
                  </div>
                </Popup>
              </CircleMarker>
            ))}

            {/* Drillhole markers */}
            {selectedLayer === 'drillholes' && drillholes.map(drillhole => (
              <CircleMarker
                key={drillhole.id}
                center={[21.0 + (drillhole.mine_id * 0.1) + (Math.random() * 0.03), 79.0 + (drillhole.mine_id * 0.1) + (Math.random() * 0.03)]}
                radius={5}
                color="#8b5cf6"
                fillColor="#8b5cf6"
                fillOpacity={0.7}
              >
                <Popup>
                  <div>
                    <strong>Drillhole: {drillhole.hole_id}</strong>
                    <p>Mine: {drillhole.mine_name}</p>
                    <p>Depth: {drillhole.total_depth_m?.toFixed(1)}m</p>
                    <p>Date: {drillhole.drill_date}</p>
                    <SourceTagBadge sourceTag={drillhole.source_tag} />
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>

        {/* Target List Panel */}
        <div className="target-panel">
          <h3>Ranked Exploration Targets</h3>
          <div className="target-list">
            {reservePredictions
              .sort((a, b) => b.predicted_reserve_tonnes - a.predicted_reserve_tonnes)
              .slice(0, 10)
              .map(prediction => {
                const mine = mines.find(m => m.id === prediction.mine_id);
                return (
                  <div 
                    key={prediction.id}
                    className={`target-item ${selectedPrediction?.id === prediction.id ? 'selected' : ''}`}
                    onClick={() => handlePredictionClick(prediction)}
                  >
                    <div className="target-header">
                      <span className="target-mine">{mine?.name || 'Unknown Mine'}</span>
                      <span className="target-confidence">
                        {(prediction.confidence_level * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="target-details">
                      <span>Predicted: {prediction.predicted_reserve_tonnes?.toFixed(2)} tonnes</span>
                      <SourceTagBadge sourceTag={prediction.source_tag} />
                    </div>
                  </div>
                );
              })}
          </div>
          <SourceTagBadge sourceTag="SYNTHETIC" />
        </div>
      </div>

      {/* Prediction Detail Panel */}
      {selectedPrediction && (
        <div className="detail-panel">
          <h3>Target Details</h3>
          <div className="detail-content">
            <div className="detail-section">
              <h4>Prediction Summary</h4>
              <p>Predicted Reserve: {selectedPrediction.predicted_reserve_tonnes?.toFixed(2)} tonnes</p>
              <p>Confidence Level: {(selectedPrediction.confidence_level * 100).toFixed(0)}%</p>
              <p>Model Version: {selectedPrediction.model_version}</p>
              <SourceTagBadge sourceTag={selectedPrediction.source_tag} />
            </div>

            {explanations.length > 0 && (
              <div className="detail-section">
                <h4>Contributing Factors</h4>
                <div className="explanations-list">
                  {explanations.map(expl => (
                    <div key={expl.id} className="explanation-item">
                      <span className="feature-name">{expl.feature_name}</span>
                      <span className="feature-value">{expl.feature_value?.toFixed(4)}</span>
                      <span className="feature-importance">
                        Importance: {(expl.importance_score * 100).toFixed(1)}%
                      </span>
                      <SourceTagBadge sourceTag={expl.source_tag} />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ExplorationDashboard;
