import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import OverviewDashboard from './pages/OverviewDashboard';
import GeologicalView from './pages/GeologicalView';
import FleetOperations from './pages/FleetOperations';
import SatelliteDashboard from './pages/SatelliteDashboard';
import ModelExplanation from './pages/ModelExplanation';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* 1. Landing Page */}
          <Route path="/" element={<LandingPage />} />

          {/* 2. Login Page */}
          <Route path="/login" element={<LoginPage />} />

          {/* 3. Executive Dashboard */}
          <Route path="/dashboard" element={<OverviewDashboard />} />
          <Route path="/overview" element={<Navigate to="/dashboard" replace />} />

          {/* 4. Geological View */}
          <Route path="/geological" element={<GeologicalView />} />
          <Route path="/exploration" element={<Navigate to="/geological" replace />} />

          {/* 5. Fleet Operations */}
          <Route path="/fleet" element={<FleetOperations />} />
          <Route path="/production" element={<Navigate to="/fleet" replace />} />

          {/* Additional Analytics */}
          <Route path="/satellite" element={<SatelliteDashboard />} />
          <Route path="/explanation" element={<ModelExplanation />} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
