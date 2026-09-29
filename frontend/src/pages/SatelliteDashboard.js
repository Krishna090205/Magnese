import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, Popup, CircleMarker } from 'react-leaflet';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import SourceTagBadge from '../components/SourceTagBadge';

const API_BASE = 'http://localhost:8000';

function SatelliteDashboard() {
  const [mines, setMines] = useState([]);
  const [selectedLayer, setSelectedLayer] = useState('rainfall');
  const [envData, setEnvData] = useState([]);
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [selectedMine, setSelectedMine] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [dateRange, setDateRange] = useState({ start: null, end: null });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const layers = ['rainfall', 'soil_moisture', 'ndvi', 'lst'];

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Fetch mines
      const minesRes = await axios.get(`${API_BASE}/api/mines`);
      setMines(minesRes.data);
      
      // Fetch environmental data for selected layer
      const envRes = await axios.get(`${API_BASE}/api/environment/${selectedLayer}?limit=100`);
      setEnvData(envRes.data);
      
      // Fetch time series data for selected mine
      if (selectedMine) {
        const tsRes = await axios.get(
          `${API_BASE}/api/environment/${selectedLayer}?mine_id=${selectedMine}&limit=365`
        );
        setTimeSeriesData(tsRes.data);
        
        // Set date range from time series data
        if (tsRes.data.length > 0) {
          const dates = tsRes.data.map(d => new Date(d.observation_date));
          setDateRange({
            start: new Date(Math.min(...dates)),
            end: new Date(Math.max(...dates))
          });
          setSelectedDate(new Date(Math.max(...dates))); // Default to latest date
        }
      }
      
      setLoading(false);
      
    } catch (err) {
      console.error('Error fetching satellite data:', err);
      setError('Failed to load satellite data');
      setLoading(false);
    }
  }, [selectedLayer, selectedMine]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getLayerColor = (layer) => {
    const colors = {
      'rainfall': '#6366f1',
      'soil_moisture': '#3b82f6',
      'ndvi': '#22c55e',
      'lst': '#f59e0b'
    };
    return colors[layer] || '#6366f1';
  };

  const getLayerUnit = (layer) => {
    const units = {
      'rainfall': 'mm',
      'soil_moisture': 'm³/m³',
      'ndvi': 'index',
      'lst': 'K'
    };
    return units[layer] || '';
  };

  if (loading) {
    return <div className="loading">Loading satellite dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h2>Satellite & Environmental Data</h2>
        <SourceTagBadge sourceTag="SYNTHETIC" size="large" />
      </div>

      <div className="satellite-layout">
        {/* Layer Controls */}
        <div className="layer-controls">
          <h4>Environmental Layers</h4>
          <div className="layer-buttons">
            {layers.map(layer => (
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

        {/* Map Section */}
        <div className="map-section">
          <MapContainer center={[21.5, 79.5]} zoom={8} style={{ height: '400px', width: '100%' }}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; OpenStreetMap contributors'
            />
            
            {/* Mine locations with environmental data points */}
            {envData.map(obs => {
              const mine = mines.find(m => m.id === obs.mine_id);
              if (!mine) return null;
              return (
                <CircleMarker
                  key={`${obs.id}-${obs.mine_id}`}
                  center={[21.0 + (obs.mine_id * 0.1), 79.0 + (obs.mine_id * 0.1)]}
                  radius={5 + (obs.value / 10)}
                  color={getLayerColor(selectedLayer)}
                  fillColor={getLayerColor(selectedLayer)}
                  fillOpacity={0.6}
                >
                  <Popup>
                    <div>
                      <strong>{mine.name}</strong>
                      <p>Date: {obs.observation_date}</p>
                      <p>Value: {obs.value.toFixed(2)} {getLayerUnit(selectedLayer)}</p>
                      <SourceTagBadge sourceTag={obs.source_tag} />
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
          </MapContainer>
          <SourceTagBadge sourceTag="SYNTHETIC" />
        </div>

        {/* Time Series Chart */}
        <div className="chart-section">
          <h3>Time Series - {selectedLayer.replace('_', ' ').toUpperCase()}</h3>
          <div className="mine-selector">
            <label>Select Mine:</label>
            <select 
              value={selectedMine || ''} 
              onChange={(e) => setSelectedMine(parseInt(e.target.value))}
            >
              <option value="">All Mines</option>
              {mines.map(mine => (
                <option key={mine.id} value={mine.id}>{mine.name}</option>
              ))}
            </select>
          </div>
          
          {/* Time Slider */}
          {dateRange.start && dateRange.end && (
            <div className="time-slider">
              <label>Time Slider:</label>
              <input
                type="range"
                min={dateRange.start.getTime()}
                max={dateRange.end.getTime()}
                value={selectedDate ? selectedDate.getTime() : dateRange.end.getTime()}
                onChange={(e) => setSelectedDate(new Date(parseInt(e.target.value)))}
                className="slider"
              />
              <span className="date-display">
                {selectedDate ? selectedDate.toLocaleDateString() : 'Select a date'}
              </span>
            </div>
          )}
          
          {timeSeriesData.length > 0 ? (
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="observation_date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke={getLayerColor(selectedLayer)} 
                    name={`${selectedLayer} (${getLayerUnit(selectedLayer)})`}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="no-data">Select a mine to view time series data</p>
          )}
          <SourceTagBadge sourceTag="SYNTHETIC" />
        </div>
      </div>

      {/* Data Summary */}
      <div className="data-summary">
        <h3>Data Summary</h3>
        <div className="summary-stats">
          <div className="stat-item">
            <span className="stat-label">Total Records:</span>
            <span className="stat-value">{envData.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Layer:</span>
            <span className="stat-value">{selectedLayer.toUpperCase()}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Unit:</span>
            <span className="stat-value">{getLayerUnit(selectedLayer)}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Mines Covered:</span>
            <span className="stat-value">{[...new Set(envData.map(d => d.mine_id))].length}</span>
          </div>
        </div>
        <SourceTagBadge sourceTag="SYNTHETIC" />
      </div>
    </div>
  );
}

export default SatelliteDashboard;
