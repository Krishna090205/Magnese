import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [authMode, setAuthMode] = useState('employee'); // 'employee' or 'sso'
  const [employeeId, setEmployeeId] = useState('officer.moil@nic.in');
  const [password, setPassword] = useState('••••••••••••');
  const [showPassword, setShowPassword] = useState(false);
  const [mfaEnabled, setMfaEnabled] = useState(true);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignIn = (e) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      localStorage.setItem('armpi_auth', JSON.stringify({
        user: employeeId,
        role: 'Chief Mining Engineer',
        time: new Date().toISOString()
      }));
      navigate('/dashboard');
    }, 500);
  };

  return (
    <div className="armpi-login-viewport">
      {/* Background Image: Mine with Engraved Rock Monument */}
      <img 
        src="/assets/login_monument.jpg" 
        alt="Minerals for a Stronger India" 
        className="login-bg-photo"
      />

      {/* Top Header */}
      <header className="login-top-bar">
        <div className="brand-group-login" onClick={() => navigate('/')}>
          <div className="moil-logo-badge">MOIL</div>
          <div className="brand-texts">
            <span className="brand-title">ARMPI</span>
            <span className="brand-subtitle">Autonomous Manganese Reserve & Production Intelligence</span>
          </div>
        </div>

        <div className="lang-selector-pill">
          <span className="globe-icon">🌐</span>
          <span>English</span>
          <span className="caret-down">⌄</span>
        </div>
      </header>

      {/* Bottom Left Branding Statement */}
      <div className="login-bottom-left-statement">
        <h3 className="statement-line">Secure</h3>
        <h3 className="statement-line">Sustainable</h3>
        <h3 className="statement-line accent">Smarter Mining</h3>
        <div className="statement-divider"></div>
        <div className="moil-enterprise-tag">
          <strong>MOIL Limited</strong>
          <span>A Government of India Enterprise</span>
        </div>
      </div>

      {/* Centered / Right-Center Frosted Glass Card */}
      <div className="login-card-floating-wrap">
        <div className="login-frosted-card">
          <div className="frosted-header">
            <h2>Welcome Back</h2>
            <p>Sign in to your ARMPI Operations Portal</p>
          </div>

          {/* Segmented Control */}
          <div className="auth-segmented-switch">
            <button 
              type="button"
              className={`seg-btn ${authMode === 'employee' ? 'active' : ''}`}
              onClick={() => setAuthMode('employee')}
            >
              Employee Login
            </button>
            <button 
              type="button"
              className={`seg-btn ${authMode === 'sso' ? 'active' : ''}`}
              onClick={() => setAuthMode('sso')}
            >
              SSO (Gov)
            </button>
          </div>

          <form onSubmit={handleSignIn} className="frosted-form">
            {/* Input 1: Employee ID / Government Email */}
            <div className="frosted-input-group">
              <span className="field-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </span>
              <input 
                type="text" 
                placeholder="Employee ID / Government Email"
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                required
              />
            </div>

            {/* Input 2: Password */}
            <div className="frosted-input-group">
              <span className="field-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </span>
              <input 
                type={showPassword ? 'text' : 'password'} 
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button 
                type="button" 
                className="eye-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
            </div>

            {/* Multi-Factor Authentication Row */}
            <div className="mfa-toggle-row">
              <label className="mfa-switch-pill">
                <input 
                  type="checkbox" 
                  checked={mfaEnabled} 
                  onChange={(e) => setMfaEnabled(e.target.checked)}
                />
                <span className="slider-round"></span>
              </label>
              <div className="mfa-labels">
                <span className="mfa-primary">Multi-Factor Authentication (MFA)</span>
                <span className="mfa-secondary">Use OTP / Authenticator App</span>
              </div>
            </div>

            {/* Sign In Button */}
            <button type="submit" className="btn-signin-pill" disabled={loading}>
              {loading ? 'Authenticating...' : 'Sign In →'}
            </button>

            {/* Forgot Password Link */}
            <div className="forgot-password-wrap">
              <a href="#forgot" className="forgot-link">Forgot Password?</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
