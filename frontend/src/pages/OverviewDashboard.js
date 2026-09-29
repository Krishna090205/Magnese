import React, { useState } from 'react';
import EnterpriseLayout from '../components/EnterpriseLayout';

const OverviewDashboard = () => {
  const [activeLayers, setActiveLayers] = useState({
    oreGrade: true,
    haulRoads: true,
    fleetLive: true,
    geologicalBlocks: false
  });
  const [dimensionMode, setDimensionMode] = useState('3D');

  const toggleLayer = (key) => {
    setActiveLayers(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <EnterpriseLayout 
      pageTitle="Good Morning, Krishna" 
      pageSubtitle="Here's what's happening at Balaghat Mine today."
      selectedMineId={2}
    >
      <div className="dashboard-content-screen">
        {/* Row of 4 Clean KPI Cards */}
        <div className="dashboard-kpi-row-4">
          {/* Card 1 */}
          <div className="dash-kpi-card">
            <div className="kpi-icon-square blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="2">
                <rect x="1" y="3" width="15" height="13" rx="2"/>
                <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
                <circle cx="5.5" cy="18.5" r="2.5"/>
                <circle cx="18.5" cy="18.5" r="2.5"/>
              </svg>
            </div>
            <div className="kpi-details">
              <div className="kpi-main-number">33,000 T</div>
              <div className="kpi-desc-label">Current Shift Output</div>
              <span className="kpi-badge-tag green">↑ 6%</span>
            </div>
          </div>

          {/* Card 2 */}
          <div className="dash-kpi-card">
            <div className="kpi-icon-square teal">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0d9488" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <div className="kpi-details">
              <div className="kpi-main-number">-8.2%</div>
              <div className="kpi-desc-label">Shortfall Risk</div>
              <span className="kpi-badge-tag green">On Track</span>
            </div>
          </div>

          {/* Card 3 */}
          <div className="dash-kpi-card">
            <div className="kpi-icon-square indigo">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <div className="kpi-details">
              <div className="kpi-main-number">94%</div>
              <div className="kpi-desc-label">Equipment Health</div>
              <span className="kpi-badge-tag green">↑ 2%</span>
            </div>
          </div>

          {/* Card 4 */}
          <div className="dash-kpi-card">
            <div className="kpi-icon-square amber">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#d97706" strokeWidth="2">
                <circle cx="12" cy="12" r="5"/>
                <line x1="12" y1="1" x2="12" y2="3"/>
                <line x1="12" y1="21" x2="12" y2="23"/>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                <line x1="1" y1="12" x2="3" y2="12"/>
                <line x1="21" y1="12" x2="23" y2="12"/>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
              </svg>
            </div>
            <div className="kpi-details">
              <div className="kpi-main-number">28°C</div>
              <div className="kpi-desc-label">Clear Weather</div>
            </div>
          </div>
        </div>

        {/* Central Map / Mine Visualization Container */}
        <div className="dashboard-map-viewport">
          <img 
            src="/assets/dashboard_mine.jpg" 
            alt="Balaghat Mine Pit Overview" 
            className="pit-map-image"
          />

          {/* Left Vertical Map Controls */}
          <div className="map-vertical-tools">
            <button className="tool-round-btn">+</button>
            <button className="tool-round-btn">-</button>
            <button className="tool-round-btn">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="12 2 19 21 12 17 5 21 12 2"/>
              </svg>
            </button>
            <button className="tool-round-btn">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="12 2 2 7 12 12 22 7 12 2"/>
              </svg>
            </button>
          </div>

          {/* Interactive Benches Pins */}
          <div className="bench-pin-marker north-bench" style={{ top: '24%', left: '48%' }}>
            <div className="pin-pulse-dot"></div>
            <div className="bench-pin-card">
              <span className="bench-name">North Bench</span>
              <span className="bench-grade">Mn Grade: 46.2%</span>
            </div>
          </div>

          <div className="bench-pin-marker central-pit" style={{ bottom: '26%', right: '32%' }}>
            <div className="pin-pulse-dot"></div>
            <div className="bench-pin-card">
              <span className="bench-name">Central Pit</span>
              <span className="bench-grade">Mn Grade: 41.8%</span>
            </div>
          </div>

          {/* Top Right Floating Layer Selector Card */}
          <div className="floating-layers-selector-card">
            <label className="layer-item-checkbox">
              <input 
                type="checkbox" 
                checked={activeLayers.oreGrade} 
                onChange={() => toggleLayer('oreGrade')}
              />
              <span className="checkbox-custom">✓</span>
              <span className="layer-item-text">Ore Grade</span>
            </label>

            <label className="layer-item-checkbox">
              <input 
                type="checkbox" 
                checked={activeLayers.haulRoads} 
                onChange={() => toggleLayer('haulRoads')}
              />
              <span className="checkbox-custom">✓</span>
              <span className="layer-item-text">Haul Roads</span>
            </label>

            <label className="layer-item-checkbox">
              <input 
                type="checkbox" 
                checked={activeLayers.fleetLive} 
                onChange={() => toggleLayer('fleetLive')}
              />
              <span className="checkbox-custom">✓</span>
              <span className="layer-item-text">Fleet Live</span>
            </label>

            <label className="layer-item-checkbox">
              <input 
                type="checkbox" 
                checked={activeLayers.geologicalBlocks} 
                onChange={() => toggleLayer('geologicalBlocks')}
              />
              <span className="checkbox-custom">{activeLayers.geologicalBlocks ? '✓' : ''}</span>
              <span className="layer-item-text">Geological Blocks</span>
            </label>
          </div>

          {/* Bottom Right 2D / 3D Switch Pill */}
          <div className="dimension-toggle-pill">
            <button 
              className={`dim-btn ${dimensionMode === '2D' ? 'active' : ''}`}
              onClick={() => setDimensionMode('2D')}
            >
              2D
            </button>
            <button 
              className={`dim-btn ${dimensionMode === '3D' ? 'active' : ''}`}
              onClick={() => setDimensionMode('3D')}
            >
              3D
            </button>
          </div>
        </div>
      </div>
    </EnterpriseLayout>
  );
};

export default OverviewDashboard;
