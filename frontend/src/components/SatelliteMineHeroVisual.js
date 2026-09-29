import React, { useRef, useEffect, useState } from 'react';

const SatelliteMineHeroVisual = () => {
  const canvasRef = useRef(null);
  const [activeBand, setActiveBand] = useState('multispectral'); // 'multispectral', 'thermal', 'sar'
  const animationFrameRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = (canvas.width = canvas.parentElement.clientWidth || 550);
    const height = (canvas.height = canvas.parentElement.clientHeight || 420);

    let angle = 0;
    let scanY = 0;
    let scanDirection = 1;

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Gradient background with gentle dark navy to soft royal tint
      const grad = ctx.createRadialGradient(width / 2, height / 2, 40, width / 2, height / 2, width * 0.7);
      grad.addColorStop(0, '#ffffff');
      grad.addColorStop(0.7, '#f1f5f9');
      grad.addColorStop(1, '#e2e8f0');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      // Coordinate Target Reticle
      const cx = width / 2;
      const cy = height / 2 + 10;

      // Radar Range Rings
      ctx.save();
      ctx.strokeStyle = 'rgba(37, 99, 235, 0.15)';
      ctx.lineWidth = 1;
      [60, 110, 160, 210].forEach(r => {
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.stroke();
      });

      // Target Crosshairs
      ctx.beginPath();
      ctx.moveTo(cx - 230, cy);
      ctx.lineTo(cx + 230, cy);
      ctx.moveTo(cx, cy - 190);
      ctx.lineTo(cx, cy + 190);
      ctx.stroke();
      ctx.restore();

      // Topographic Contour Lines of Manganese Pit
      ctx.save();
      ctx.strokeStyle = activeBand === 'multispectral' 
        ? 'rgba(30, 58, 138, 0.45)' 
        : (activeBand === 'thermal' ? 'rgba(217, 119, 6, 0.45)' : 'rgba(16, 185, 129, 0.45)');
      ctx.lineWidth = 1.5;

      for (let i = 1; i <= 6; i++) {
        ctx.beginPath();
        const rx = 180 - i * 22;
        const ry = 110 - i * 14;
        ctx.ellipse(cx, cy, rx, ry, 0.25, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.restore();

      // Core Manganese Ore Zone in Center Pit
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(cx + 10, cy - 5, 45, 26, 0.25, 0, Math.PI * 2);
      ctx.fillStyle = activeBand === 'multispectral' 
        ? 'rgba(49, 46, 129, 0.75)' 
        : (activeBand === 'thermal' ? 'rgba(239, 68, 68, 0.7)' : 'rgba(16, 185, 129, 0.7)');
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Label on Ore anomaly
      ctx.font = 'bold 9px Inter, sans-serif';
      ctx.fillStyle = '#ffffff';
      ctx.fillText('Mn ORE VEIN', cx - 18, cy - 2);
      ctx.font = '8px Inter, sans-serif';
      ctx.fillText('Grade: 44.2%', cx - 14, cy + 9);
      ctx.restore();

      // Moving Satellite Scanning Beam
      scanY += scanDirection * 1.2;
      if (scanY > height - 60 || scanY < 40) scanDirection *= -1;

      ctx.save();
      const beamGrad = ctx.createLinearGradient(0, scanY - 30, 0, scanY + 30);
      beamGrad.addColorStop(0, 'rgba(59, 130, 246, 0)');
      beamGrad.addColorStop(0.5, 'rgba(37, 99, 235, 0.22)');
      beamGrad.addColorStop(1, 'rgba(59, 130, 246, 0)');
      ctx.fillStyle = beamGrad;
      ctx.fillRect(40, scanY - 20, width - 80, 40);

      ctx.beginPath();
      ctx.moveTo(40, scanY);
      ctx.lineTo(width - 40, scanY);
      ctx.strokeStyle = '#2563eb';
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.restore();

      // Satellite Orbital Path & Indicator at Top Right
      angle += 0.012;
      const satX = cx + Math.cos(angle) * 190;
      const satY = cy - 130 + Math.sin(angle) * 30;

      ctx.save();
      // Satellite Icon
      ctx.beginPath();
      ctx.arc(satX, satY, 5, 0, Math.PI * 2);
      ctx.fillStyle = '#1e3a8a';
      ctx.fill();
      ctx.strokeStyle = '#60a5fa';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Solar Panels
      ctx.fillStyle = '#3b82f6';
      ctx.fillRect(satX - 14, satY - 2, 7, 4);
      ctx.fillRect(satX + 7, satY - 2, 7, 4);

      // Radar Pulse Wave from Satellite
      ctx.beginPath();
      ctx.arc(satX, satY, 18, 0.3, Math.PI - 0.3);
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.6)';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      ctx.font = 'bold 9px Inter, sans-serif';
      ctx.fillStyle = '#0f2b5c';
      ctx.fillText('SENTINEL-2B / LANDSAT-9', satX - 55, satY - 14);
      ctx.font = '8px Inter, sans-serif';
      ctx.fillStyle = '#2563eb';
      ctx.fillText('Cross-Sensor Swath Active', satX - 55, satY - 5);
      ctx.restore();

      animationFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [activeBand]);

  return (
    <div className="satellite-hero-card">
      <div className="satellite-hud-top">
        <div className="badge-orbit">
          <span className="live-dot-green"></span>
          ORBITAL GEO-SCANNING
        </div>
        <div className="band-toggles">
          <button 
            className={`band-btn ${activeBand === 'multispectral' ? 'active' : ''}`}
            onClick={() => setActiveBand('multispectral')}
          >
            Multispectral (NDVI/Bores)
          </button>
          <button 
            className={`band-btn ${activeBand === 'thermal' ? 'active' : ''}`}
            onClick={() => setActiveBand('thermal')}
          >
            Thermal IR (LST)
          </button>
          <button 
            className={`band-btn ${activeBand === 'sar' ? 'active' : ''}`}
            onClick={() => setActiveBand('sar')}
          >
            Sentinel-1 SAR
          </button>
        </div>
      </div>

      <div className="hero-canvas-container">
        <canvas ref={canvasRef} />
        
        {/* Floating live spatial telemetry tag */}
        <div className="telemetry-corner-tag">
          <div className="tag-line"><strong>TARGET:</strong> Balaghat-Nagpur Manganese Orogeny</div>
          <div className="tag-line"><strong>COORDS:</strong> 21°55'42" N • 79°41'20" E</div>
          <div className="tag-line"><strong>SPECTRAL RESOLUTION:</strong> 10m Pixel Band</div>
        </div>
      </div>
    </div>
  );
};

export default SatelliteMineHeroVisual;
