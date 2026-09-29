import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import OverviewDashboard from './pages/OverviewDashboard';
import ExplorationDashboard from './pages/ExplorationDashboard';
import ProductionDashboard from './pages/ProductionDashboard';
import SatelliteDashboard from './pages/SatelliteDashboard';
import ModelExplanation from './pages/ModelExplanation';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-brand">
            <h1>MOIL Manganese Exploration System</h1>
            <span className="stage-badge">Stage 3</span>
          </div>
          <div className="nav-links">
            <Link to="/" className="nav-link">Overview</Link>
            <Link to="/exploration" className="nav-link">Exploration</Link>
            <Link to="/production" className="nav-link">Production</Link>
            <Link to="/satellite" className="nav-link">Satellite</Link>
            <Link to="/explanation" className="nav-link">Model Explanation</Link>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<OverviewDashboard />} />
            <Route path="/exploration" element={<ExplorationDashboard />} />
            <Route path="/production" element={<ProductionDashboard />} />
            <Route path="/satellite" element={<SatelliteDashboard />} />
            <Route path="/explanation" element={<ModelExplanation />} />
          </Routes>
        </main>

        <footer className="footer">
          <div className="footer-content">
            <p>MOIL Manganese Reserve Targeting & Production Shortfall Early Warning System</p>
            <p className="data-disclaimer">
              Data Source Tags: <span className="tag real-official">REAL_OFFICIAL</span> 
              <span className="tag real-public">REAL_PUBLIC</span> 
              <span className="tag proxy">PROXY</span> 
              <span className="tag synthetic">SYNTHETIC</span>
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
