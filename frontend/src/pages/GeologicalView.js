import React, { useState } from 'react';
import EnterpriseLayout from '../components/EnterpriseLayout';

const GeologicalView = () => {
  const [layers, setLayers] = useState({
    sentinel2: true,
    hyperspectral: true,
    thermal: false,
    borehole3d: true,
    boundaries: true,
    contours: false,
    dem: false
  });

  const toggleLayer = (key) => {
    setLayers(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <EnterpriseLayout 
      pageTitle="Geological & Satellite View" 
      pageSubtitle="Analyze satellite data and geological models for accurate reserve estimation."
      selectedMineId={2}
    >
      <div className="geological-screen-layout">
        {/* Left Column: Layers Card & 3D Ore Grade Model Card */}
        <aside className="geological-left-sidebar">
          {/* Layers Checklist Card */}
          <div className="geo-layers-card">
            <h4 className="geo-card-heading">
              <span className="heading-icon">📑</span>
              Layers
            </h4>

            <div className="geo-checklist">
              <label className="geo-checkbox-row">
                <input 
                  type="checkbox" 
                  checked={layers.sentinel2} 
                  onChange={() => toggleLayer('sentinel2')}
                />
                <span className={`custom-chk ${layers.sentinel2 ? 'checked' : ''}`}>
                  {layers.sentinel2 && '✓'}
                </span>
                <span className="chk-label">Satellite Imagery (Sentinel-2)</span>
              </label>

              <label className="geo-checkbox-row">
                <input 
                  type="checkbox" 
                  checked={layers.hyperspectral} 
                  onChange={() => toggleLayer('hyperspectral')}
                />
                <span className={`custom-chk ${layers.hyperspectral ? 'checked' : ''}`}>
                  {layers.hyperspectral && '✓'}
                </span>
                <span className="chk-label">SWIR/VNIR Hyperspectral</span>
              </label>

              <label className="geo-checkbox-row">
                <input 
                  type="checkbox" 
                  checked={layers.thermal} 
                  onChange={() => toggleLayer('thermal')}
                />
                <span className={`custom-chk ${layers.thermal ? 'checked' : ''}`}>
                  {layers.thermal && '✓'}
                </span>
                <span className="chk-label">Thermal Overburden Index</span>
              </label>

              <label className="geo-checkbox-row">
                <input 
                  type="checkbox" 
                  checked={layers.borehole3d} 
                  onChange={() => toggleLayer('borehole3d')}
                />
                <span className={`custom-chk ${layers.borehole3d ? 'checked' : ''}`}>
                  {layers.borehole3d && '✓'}
                </span>
                <span className="chk-label">Borehole Assay (3D)</span>
              </label>

              <label className="geo-checkbox-row">
                <input 
                  type="checkbox" 
                  checked={layers.boundaries} 
                  onChange={() => toggleLayer('boundaries')}
                />
                <span className={`custom-chk ${layers.boundaries ? 'checked' : ''}`}>
                  {layers.boundaries && '✓'}
                </span>
                <span className="chk-label">Geological Boundaries</span>
              </label>

              <label className="geo-checkbox-row">
                <input 
                  type="checkbox" 
                  checked={layers.contours} 
                  onChange={() => toggleLayer('contours')}
                />
                <span className={`custom-chk ${layers.contours ? 'checked' : ''}`}>
                  {layers.contours && '✓'}
                </span>
                <span className="chk-label">Ore-Grade Contours</span>
              </label>

              <label className="geo-checkbox-row">
                <input 
                  type="checkbox" 
                  checked={layers.dem} 
                  onChange={() => toggleLayer('dem')}
                />
                <span className={`custom-chk ${layers.dem ? 'checked' : ''}`}>
                  {layers.dem && '✓'}
                </span>
                <span className="chk-label">Topographic DEM</span>
              </label>
            </div>
          </div>

          {/* 3D Ore Grade Model Gradient Card */}
          <div className="geo-grade-card">
            <h4 className="geo-card-heading">3D Ore Grade Model</h4>
            <div className="grade-legend-block">
              <span className="grade-label">Mn Grade (%)</span>
              {/* Continuous multi-stop spectrum bar */}
              <div className="continuous-spectrum-bar"></div>
              <div className="spectrum-scale-labels">
                <span>&lt; 30</span>
                <span>30 - 40</span>
                <span>40 - 45</span>
                <span>&gt; 45</span>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Center Area: 3D Voxel Ore Body Mine View */}
        <div className="geological-main-viewport">
          <div className="geo-canvas-card">
            <img 
              src="/assets/geological_ore.jpg" 
              alt="3D Ore Grade Voxel Model" 
              className="geo-voxel-image"
            />

            {/* Top Right Map Tool Controls */}
            <div className="geo-top-right-tools">
              <button className="tool-round-btn">+</button>
              <button className="tool-round-btn">-</button>
              <button className="tool-round-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="12 2 2 7 12 12 22 7 12 2"/>
                  <polyline points="2 17 12 22 22 17"/>
                  <polyline points="2 12 12 17 22 12"/>
                </svg>
              </button>
            </div>

            {/* Bottom Right Preview Thumbnails */}
            <div className="geo-bottom-right-previews">
              <div className="preview-thumb active" title="Stratigraphic Core View">
                <img src="/assets/dashboard_mine.jpg" alt="Bench View" />
              </div>
              <div className="preview-thumb" title="Voxel Block Cutaway">
                <img src="/assets/landing_mine.jpg" alt="Voxel Wireframe" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </EnterpriseLayout>
  );
};

export default GeologicalView;
