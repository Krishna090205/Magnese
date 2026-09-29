import React, { useState } from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import { MOIL_MINES } from '../data/mockData';

const EnterpriseLayout = ({ children, selectedMineId = 2, onSelectMine, pageTitle, pageSubtitle }) => {
  const [selectedMine, setSelectedMine] = useState(selectedMineId);
  const location = useLocation();

  const handleMineChange = (id) => {
    setSelectedMine(id);
    if (onSelectMine) onSelectMine(id);
  };

  const activeMineObj = MOIL_MINES.find(m => m.id === selectedMine) || MOIL_MINES[1]; // Balaghat default as in reference

  return (
    <div className="armpi-app-shell">
      {/* Slim Clean Sidebar */}
      <aside className="app-sidebar-slim">
        <Link to="/" className="sidebar-brand-head">
          <div className="moil-logo-circle">MOIL</div>
          <span className="sidebar-brand-title">ARMPI</span>
        </Link>

        <nav className="sidebar-nav-list">
          <NavLink 
            to="/dashboard" 
            className={({ isActive }) => `side-nav-btn ${isActive || location.pathname === '/overview' ? 'active' : ''}`}
          >
            <span className="side-nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
            </span>
            <span className="side-nav-text">Dashboard</span>
          </NavLink>

          <NavLink 
            to="/geological" 
            className={({ isActive }) => `side-nav-btn ${isActive || location.pathname === '/exploration' ? 'active' : ''}`}
          >
            <span className="side-nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="12 2 2 7 12 12 22 7 12 2"/>
                <polyline points="2 17 12 22 22 17"/>
                <polyline points="2 12 12 17 22 12"/>
              </svg>
            </span>
            <span className="side-nav-text">Geological</span>
          </NavLink>

          <NavLink 
            to="/fleet" 
            className={({ isActive }) => `side-nav-btn ${isActive ? 'active' : ''}`}
          >
            <span className="side-nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="1" y="3" width="15" height="13" rx="2"/>
                <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
                <circle cx="5.5" cy="18.5" r="2.5"/>
                <circle cx="18.5" cy="18.5" r="2.5"/>
              </svg>
            </span>
            <span className="side-nav-text">Fleet Operations</span>
          </NavLink>

          <NavLink 
            to="/production" 
            className={({ isActive }) => `side-nav-btn ${isActive ? 'active' : ''}`}
          >
            <span className="side-nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="20" x2="18" y2="10"/>
                <line x1="12" y1="20" x2="12" y2="4"/>
                <line x1="6" y1="20" x2="6" y2="14"/>
              </svg>
            </span>
            <span className="side-nav-text">Production</span>
          </NavLink>

          <NavLink 
            to="/explanation" 
            className={({ isActive }) => `side-nav-btn ${isActive ? 'active' : ''}`}
          >
            <span className="side-nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </span>
            <span className="side-nav-text">AI Advisory</span>
          </NavLink>

          <NavLink 
            to="/satellite" 
            className={({ isActive }) => `side-nav-btn ${isActive ? 'active' : ''}`}
          >
            <span className="side-nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
            </span>
            <span className="side-nav-text">Settings</span>
          </NavLink>
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="app-main-viewport">
        {/* Top Header */}
        <header className="app-top-header">
          <div className="header-greeting-box">
            <h2 className="greeting-title">{pageTitle || "Good Morning, Krishna"}</h2>
            <p className="greeting-subtitle">
              {pageSubtitle || `Here's what's happening at ${activeMineObj.name} today.`}
            </p>
          </div>

          <div className="header-right-tools">
            {/* Mine Selector Dropdown Pill */}
            <div className="mine-select-pill">
              <span className="location-pin-icon">📍</span>
              <select 
                value={selectedMine} 
                onChange={(e) => handleMineChange(parseInt(e.target.value))}
                className="mine-dropdown-native"
              >
                {MOIL_MINES.map(m => (
                  <option key={m.id} value={m.id}>{m.name}</option>
                ))}
              </select>
              <span className="caret-icon">⌄</span>
            </div>

            {/* Officer Avatar Circle */}
            <div className="officer-avatar-box" title="Chief Engineer Krishna">
              <img 
                src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&h=120&q=80" 
                alt="Krishna" 
                className="officer-photo"
              />
            </div>
          </div>
        </header>

        {/* Page Body */}
        <main className="app-page-content-box">
          {children}
        </main>
      </div>
    </div>
  );
};

export default EnterpriseLayout;
