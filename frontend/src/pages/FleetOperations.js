import React from 'react';
import EnterpriseLayout from '../components/EnterpriseLayout';

const FleetOperations = () => {
  return (
    <EnterpriseLayout 
      pageTitle="Fleet Operations" 
      pageSubtitle="Real-time fleet tracking, dispatch optimization and bottleneck prediction."
      selectedMineId={2}
    >
      <div className="fleet-screen-layout">
        {/* Top 4 KPI Cards */}
        <div className="dashboard-kpi-row-4">
          {/* Card 1 */}
          <div className="dash-kpi-card">
            <div className="kpi-icon-square blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="2">
                <rect x="1" y="3" width="15" height="13" rx="2"/>
                <polygon points="16 8 20 8 23 11 23 16 16 16 8"/>
                <circle cx="5.5" cy="18.5" r="2.5"/>
                <circle cx="18.5" cy="18.5" r="2.5"/>
              </svg>
            </div>
            <div className="kpi-details">
              <div className="kpi-main-number">36 / 42</div>
              <div className="kpi-desc-label">Active Fleet</div>
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
              <div className="kpi-main-number">86%</div>
              <div className="kpi-desc-label">Cycle Time Efficiency</div>
            </div>
          </div>

          {/* Card 3 */}
          <div className="dash-kpi-card">
            <div className="kpi-icon-square indigo">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" strokeWidth="2">
                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
              </svg>
            </div>
            <div className="kpi-details">
              <div className="kpi-main-number">2.4 hrs</div>
              <div className="kpi-desc-label">MTTR (Downtime)</div>
            </div>
          </div>

          {/* Card 4 */}
          <div className="dash-kpi-card">
            <div className="kpi-icon-square purple">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 14 14"/>
              </svg>
            </div>
            <div className="kpi-details">
              <div className="kpi-main-number">06 : 24 : 18</div>
              <div className="kpi-desc-label">Rain Impact (Forecast)</div>
            </div>
          </div>
        </div>

        {/* Middle Section: Haulage Flow (Main Visual) + AI Advisory Panel (Right) */}
        <div className="fleet-middle-grid">
          {/* Haulage Flow Visual Card */}
          <div className="haulage-flow-card">
            <div className="haulage-card-header">
              <h4>Haulage Flow</h4>
            </div>

            <div className="haulage-image-viewport">
              <img 
                src="/assets/fleet_haulage.jpg" 
                alt="Haulage Flow Network" 
                className="haulage-bg-img"
              />

              {/* Station Indicators */}
              <div className="station-badge green" style={{ top: '22%', left: '26%' }}>
                <span className="dot"></span>
                <span>North Bench</span>
              </div>

              <div className="station-badge blue" style={{ bottom: '28%', left: '20%' }}>
                <span className="dot"></span>
                <span>Central Pit</span>
              </div>

              <div className="station-badge dark" style={{ top: '35%', right: '18%' }}>
                <span className="dot"></span>
                <span>Crusher</span>
              </div>
            </div>
          </div>

          {/* AI Advisory Panel */}
          <div className="fleet-ai-advisory-card">
            <h4 className="advisory-heading">
              <span className="sparkle-icon">✨</span>
              AI Advisory
            </h4>

            <div className="advisory-notice-box high">
              <div className="notice-badge red">
                <span className="warning-symbol">⚠️</span>
                <span>High Priority</span>
              </div>
              <p className="notice-text">
                Reroute 4 dumpers from North Bench to avoid blasting delay.
              </p>
              <button className="btn-approve-reroute">
                Approve Re-route
              </button>
            </div>

            <div className="advisory-notice-box medium">
              <div className="notice-badge amber">
                <span className="warning-symbol">⚠️</span>
                <span>Medium</span>
              </div>
              <p className="notice-text">
                Reschedule maintenance for Excavator EX-08.
              </p>
              <button className="btn-approve-light">
                Approve
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Row: Fleet Utilization Chart + Equipment Health Progress Bars */}
        <div className="fleet-bottom-grid">
          {/* Fleet Utilization Card */}
          <div className="fleet-utilization-card">
            <div className="util-card-header">
              <h4>Fleet Utilization</h4>
              <span className="util-percentage-badge">87%</span>
            </div>

            <div className="util-barchart-container">
              {[
                { label: 'H1', height: '62%' },
                { label: 'H2', height: '80%' },
                { label: 'H3', height: '94%' },
                { label: 'H4', height: '75%' },
                { label: 'H5', height: '88%' },
                { label: 'H6', height: '68%' }
              ].map((bar, i) => (
                <div key={i} className="bar-col">
                  <div className="bar-track">
                    <div className="bar-fill" style={{ height: bar.height }}></div>
                  </div>
                  <span className="bar-label">{bar.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Equipment Health Card */}
          <div className="equipment-health-card">
            <div className="health-card-header">
              <h4>Equipment Health</h4>
            </div>

            <div className="health-bars-list">
              <div className="health-item-row">
                <div className="health-name">
                  <span className="icon">🚜</span>
                  <span>Excavators</span>
                </div>
                <div className="progress-outer">
                  <div className="progress-inner green" style={{ width: '92%' }}></div>
                </div>
                <span className="percent-val">92%</span>
              </div>

              <div className="health-item-row">
                <div className="health-name">
                  <span className="icon">🚛</span>
                  <span>Haul Trucks</span>
                </div>
                <div className="progress-outer">
                  <div className="progress-inner amber" style={{ width: '85%' }}></div>
                </div>
                <span className="percent-val">85%</span>
              </div>

              <div className="health-item-row">
                <div className="health-name">
                  <span className="icon">⚙️</span>
                  <span>Drills</span>
                </div>
                <div className="progress-outer">
                  <div className="progress-inner yellow" style={{ width: '78%' }}></div>
                </div>
                <span className="percent-val">78%</span>
              </div>

              <div className="health-item-row">
                <div className="health-name">
                  <span className="icon">🏗️</span>
                  <span>Loaders</span>
                </div>
                <div className="progress-outer">
                  <div className="progress-inner green" style={{ width: '94%' }}></div>
                </div>
                <span className="percent-val">94%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </EnterpriseLayout>
  );
};

export default FleetOperations;
