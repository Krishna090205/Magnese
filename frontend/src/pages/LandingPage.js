import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="armpi-landing-viewport">
      {/* Top Navigation Bar */}
      <header className="armpi-top-nav">
        <div className="nav-inner-container">
          <div className="brand-group">
            <div className="moil-logo-badge">MOIL</div>
            <div className="brand-texts">
              <span className="brand-title">ARMPI</span>
              <span className="brand-subtitle">Autonomous Manganese Reserve & Production Intelligence</span>
            </div>
          </div>

          <nav className="center-nav-links">
            <a href="#home" className="center-nav-link active">Home</a>
            <a href="#solutions" className="center-nav-link">Solutions</a>
            <a href="#technology" className="center-nav-link">Technology</a>
            <a href="#impact" className="center-nav-link">Impact</a>
            <a href="#about" className="center-nav-link">About</a>
          </nav>

          <div className="nav-actions">
            <Link to="/login" className="btn-nav-login">
              Login →
            </Link>
          </div>
        </div>
      </header>

      {/* Main Hero Section with Background Mine Image */}
      <main className="landing-hero-backdrop">
        <img 
          src="/assets/landing_mine.jpg" 
          alt="Autonomous Manganese Mine Satellite Intelligence" 
          className="hero-bg-photo"
        />

        {/* Translucent Left Gradient Overlay */}
        <div className="hero-left-overlay">
          <div className="hero-left-content">
            <h1 className="hero-main-title">
              AI-driven<br />
              Manganese Intelligence<br />
              for a Stronger India
            </h1>

            <p className="hero-description">
              Integrating Satellite Insights, Predictive Analytics and Real-time Mine Operations to ensure sustainable and efficient manganese production.
            </p>

            <div className="hero-cta-buttons">
              <button onClick={() => navigate('/dashboard')} className="btn-explore-platform">
                Explore Platform →
              </button>
              <button onClick={() => navigate('/geological')} className="btn-watch-video">
                <span className="play-circle-icon">▶</span>
                Watch Video
              </button>
            </div>

            {/* 3 Floating Feature Cards in a row */}
            <div className="hero-three-cards-row">
              {/* Card 1 */}
              <div className="hero-feat-card" onClick={() => navigate('/geological')}>
                <div className="feat-icon-wrap">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1e3a8a" strokeWidth="2">
                    <circle cx="12" cy="12" r="9"/>
                    <path d="M12 3v18M3 12h18"/>
                    <circle cx="12" cy="12" r="3" fill="#2563eb"/>
                  </svg>
                </div>
                <h4>Satellite Reserve Mapping</h4>
                <p>High-resolution Earth observation for accurate resource estimation.</p>
                <div className="feat-arrow-circle">→</div>
              </div>

              {/* Card 2 */}
              <div className="hero-feat-card" onClick={() => navigate('/dashboard')}>
                <div className="feat-icon-wrap">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1e3a8a" strokeWidth="2">
                    <rect x="3" y="12" width="4" height="8" rx="1" fill="#2563eb"/>
                    <rect x="10" y="8" width="4" height="12" rx="1" fill="#1e3a8a"/>
                    <rect x="17" y="4" width="4" height="16" rx="1" fill="#3b82f6"/>
                  </svg>
                </div>
                <h4>Predictive Production Intelligence</h4>
                <p>AI models to forecast shortfall risk and optimize output.</p>
                <div className="feat-arrow-circle">→</div>
              </div>

              {/* Card 3 */}
              <div className="hero-feat-card" onClick={() => navigate('/fleet')}>
                <div className="feat-icon-wrap">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1e3a8a" strokeWidth="2">
                    <rect x="1" y="3" width="15" height="13" rx="2"/>
                    <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
                    <circle cx="5.5" cy="18.5" r="2.5" fill="#1e3a8a"/>
                    <circle cx="18.5" cy="18.5" r="2.5" fill="#1e3a8a"/>
                  </svg>
                </div>
                <h4>Smart Fleet Optimization</h4>
                <p>Real-time tracking and intelligent dispatching.</p>
                <div className="feat-arrow-circle">→</div>
              </div>
            </div>
          </div>
        </div>

        {/* Floating Stat Strip at Bottom Right over the Mine Image */}
        <div className="floating-mine-stats-strip">
          <div className="mine-stat-col">
            <span className="stat-icon-svg">💎</span>
            <div className="stat-info">
              <span className="stat-val">52.8 <small>Mt</small></span>
              <span className="stat-lbl">Identified Reserves</span>
            </div>
          </div>
          <div className="stat-divider"></div>

          <div className="mine-stat-col">
            <span className="stat-icon-svg">⛏</span>
            <div className="stat-info">
              <span className="stat-val">5</span>
              <span className="stat-lbl">Active Mines</span>
            </div>
          </div>
          <div className="stat-divider"></div>

          <div className="mine-stat-col">
            <span className="stat-icon-svg">⚖</span>
            <div className="stat-info">
              <span className="stat-val">33,000 <small>T</small></span>
              <span className="stat-lbl">Daily Production</span>
            </div>
          </div>
          <div className="stat-divider"></div>

          <div className="mine-stat-col">
            <span className="stat-icon-svg">🛡</span>
            <div className="stat-info">
              <span className="stat-val">94%</span>
              <span className="stat-lbl">Model Confidence</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default LandingPage;
