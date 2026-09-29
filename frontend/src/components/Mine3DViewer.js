import React, { useRef, useEffect, useState } from 'react';

const Mine3DViewer = ({ mineName = 'Dongri Buzurg Mine', selectedBench = 'all', onSelectBench }) => {
  const canvasRef = useRef(null);
  const [rotation, setRotation] = useState({ x: 38, y: 45 });
  const [zoom, setZoom] = useState(1);
  const [autoRotate, setAutoRotate] = useState(true);
  const [activeLayer, setActiveLayer] = useState('all'); // 'all', 'ore', 'routes', 'drillholes'
  const isDraggingRef = useRef(false);
  const lastMousePosRef = useRef({ x: 0, y: 0 });
  const animationFrameRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = (canvas.width = canvas.parentElement.clientWidth || 800);
    let height = (canvas.height = canvas.parentElement.clientHeight || 450);

    const handleResize = () => {
      if (!canvas || !canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth || 800;
      height = canvas.height = canvas.parentElement.clientHeight || 450;
    };
    window.addEventListener('resize', handleResize);

    // Bench definition data
    const benches = [
      { elevation: '+340m Surface Rim', level: 0, radiusX: 320, radiusY: 170, color: '#e2e8f0', stroke: '#cbd5e1', hasOre: false },
      { elevation: '+320m Overburden', level: 1, radiusX: 280, radiusY: 148, color: '#f1f5f9', stroke: '#cbd5e1', hasOre: false },
      { elevation: '+300m Upper Bench', level: 2, radiusX: 240, radiusY: 126, color: '#e2e8f0', stroke: '#94a3b8', hasOre: false },
      { elevation: '+280m High-Grade Ore Face', level: 3, radiusX: 195, radiusY: 104, color: '#312e81', stroke: '#4338ca', hasOre: true, grade: '43.8% Mn' },
      { elevation: '+260m Main Pit Floor', level: 4, radiusX: 140, radiusY: 76, color: '#1e1b4b', stroke: '#3730a3', hasOre: true, grade: '44.5% Mn' }
    ];

    // Animated trucks on road spiral
    let truckProgress1 = 0.2;
    let truckProgress2 = 0.65;
    let truckProgress3 = 0.88;

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Soft industrial sky gradient
      const skyGrad = ctx.createLinearGradient(0, 0, 0, height);
      skyGrad.addColorStop(0, '#f8fafc');
      skyGrad.addColorStop(1, '#edf2f7');
      ctx.fillStyle = skyGrad;
      ctx.fillRect(0, 0, width, height);

      // Compass / Coordinates Grid
      ctx.save();
      ctx.strokeStyle = 'rgba(203, 213, 225, 0.4)';
      ctx.lineWidth = 1;
      const step = 40;
      for (let x = 0; x < width; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }
      ctx.restore();

      // Center point
      const cx = width / 2;
      const cy = height / 2 + 30;

      // 3D Perspective calculations
      const radY = (rotation.y * Math.PI) / 180;
      const radX = (rotation.x * Math.PI) / 180;

      // Draw Top Rim Ground Plane
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(cx, cy - 60 * zoom, 360 * zoom, 195 * zoom, radY * 0.1, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(241, 245, 249, 0.85)';
      ctx.fill();
      ctx.strokeStyle = '#94a3b8';
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.restore();

      // Draw Benches from top to bottom
      benches.forEach((bench, i) => {
        const benchY = cy + (i * 26 - 40) * zoom;
        const rx = bench.radiusX * zoom;
        const ry = bench.radiusY * zoom * Math.sin(radX);

        const isDimmed = activeLayer === 'ore' && !bench.hasOre;

        // Draw bench wall shadow
        if (i > 0) {
          ctx.beginPath();
          const prevY = cy + ((i - 1) * 26 - 40) * zoom;
          const prevRx = benches[i - 1].radiusX * zoom;
          const prevRy = benches[i - 1].radiusY * zoom * Math.sin(radX);
          ctx.ellipse(cx, prevY, prevRx, prevRy, 0, 0, Math.PI);
          ctx.ellipse(cx, benchY, rx, ry, 0, Math.PI, 0, true);
          ctx.fillStyle = bench.hasOre 
            ? 'rgba(49, 46, 129, 0.22)' 
            : 'rgba(148, 163, 184, 0.18)';
          ctx.fill();
        }

        // Draw bench surface terrace
        ctx.beginPath();
        ctx.ellipse(cx, benchY, rx, ry, 0, 0, Math.PI * 2);
        
        if (bench.hasOre) {
          const oreGrad = ctx.createRadialGradient(cx, benchY, rx * 0.2, cx, benchY, rx);
          oreGrad.addColorStop(0, '#312e81');
          oreGrad.addColorStop(0.6, '#1e1b4b');
          oreGrad.addColorStop(1, '#0f172a');
          ctx.fillStyle = oreGrad;
          ctx.fill();
          ctx.strokeStyle = '#6366f1';
          ctx.lineWidth = 2.5;
          ctx.stroke();
        } else {
          ctx.fillStyle = isDimmed ? 'rgba(226, 232, 240, 0.4)' : bench.color;
          ctx.fill();
          ctx.strokeStyle = isDimmed ? 'rgba(203, 213, 225, 0.5)' : bench.stroke;
          ctx.lineWidth = 1.2;
          ctx.stroke();
        }

        // Bench Elevation Label
        ctx.save();
        ctx.font = '10px Inter, sans-serif';
        ctx.fillStyle = bench.hasOre ? '#818cf8' : '#64748b';
        ctx.fillText(bench.elevation, cx - rx + 10, benchY - 4);
        if (bench.hasOre) {
          ctx.fillStyle = '#4ade80';
          ctx.font = 'bold 9px Inter, sans-serif';
          ctx.fillText(`● Mn Vein: ${bench.grade}`, cx - rx + 10, benchY + 9);
        }
        ctx.restore();
      });

      // Draw Haulage Spiral Road
      ctx.save();
      ctx.beginPath();
      ctx.strokeStyle = activeLayer === 'routes' ? '#2563eb' : '#94a3b8';
      ctx.lineWidth = activeLayer === 'routes' ? 3.5 : 2;
      ctx.setLineDash([6, 4]);

      const spiralSteps = 80;
      for (let s = 0; s <= spiralSteps; s++) {
        const t = s / spiralSteps;
        const curRadiusX = (310 - t * 170) * zoom;
        const curRadiusY = (165 - t * 90) * zoom * Math.sin(radX);
        const curY = cy + (-40 + t * 105) * zoom;
        const angle = t * Math.PI * 4 + radY;
        const px = cx + Math.cos(angle) * curRadiusX;
        const py = curY + Math.sin(angle) * curRadiusY;

        if (s === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.restore();

      // Moving Haul Trucks on the route
      truckProgress1 = (truckProgress1 + 0.002) % 1;
      truckProgress2 = (truckProgress2 + 0.0018) % 1;
      truckProgress3 = (truckProgress3 + 0.0022) % 1;

      const drawTruck = (t, label, status, isOreLoaded) => {
        const curRadiusX = (310 - t * 170) * zoom;
        const curRadiusY = (165 - t * 90) * zoom * Math.sin(radX);
        const curY = cy + (-40 + t * 105) * zoom;
        const angle = t * Math.PI * 4 + radY;
        const px = cx + Math.cos(angle) * curRadiusX;
        const py = curY + Math.sin(angle) * curRadiusY;

        // Truck shadow
        ctx.beginPath();
        ctx.ellipse(px, py + 4, 10 * zoom, 4 * zoom, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(15, 23, 42, 0.25)';
        ctx.fill();

        // Truck body
        ctx.beginPath();
        ctx.roundRect(px - 7 * zoom, py - 6 * zoom, 14 * zoom, 9 * zoom, 2);
        ctx.fillStyle = isOreLoaded ? '#1e3a8a' : '#d97706';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.stroke();

        // Truck Cabin
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(px + 1 * zoom, py - 5 * zoom, 4 * zoom, 4 * zoom);

        // Status tag
        ctx.font = '9px Inter, sans-serif';
        ctx.fillStyle = '#0f172a';
        ctx.fillText(label, px + 10, py - 4);
        ctx.font = '8px Inter, sans-serif';
        ctx.fillStyle = isOreLoaded ? '#1d4ed8' : '#b45309';
        ctx.fillText(status, px + 10, py + 6);
      };

      drawTruck(truckProgress1, 'HT-01', 'Hauling Mn (98T)', true);
      drawTruck(truckProgress2, 'HT-04', 'Returning Empty', false);
      drawTruck(truckProgress3, 'HT-07', 'Hauling Mn (102T)', true);

      // Primary Crusher Plant Indicator at Rim
      const crusherX = cx + 290 * zoom;
      const crusherY = cy - 70 * zoom;
      ctx.save();
      ctx.fillStyle = '#1e293b';
      ctx.beginPath();
      ctx.roundRect(crusherX - 16, crusherY - 14, 32, 28, 4);
      ctx.fill();
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Crusher Feed Hopper
      ctx.fillStyle = '#94a3b8';
      ctx.fillRect(crusherX - 8, crusherY - 6, 16, 12);
      ctx.font = 'bold 9px Inter, sans-serif';
      ctx.fillStyle = '#0f2b5c';
      ctx.fillText('PRIMARY CRUSHER #1', crusherX - 44, crusherY - 20);
      ctx.fillStyle = '#10b981';
      ctx.font = '8px Inter, sans-serif';
      ctx.fillText('● 450 T/hr Online', crusherX - 25, crusherY + 24);
      ctx.restore();

      // Shovel Extraction Station at Bottom Bench
      const shovelX = cx - 40 * zoom;
      const shovelY = cy + 55 * zoom;
      ctx.save();
      ctx.fillStyle = '#dc2626';
      ctx.beginPath();
      ctx.arc(shovelX, shovelY, 6 * zoom, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.font = 'bold 9px Inter, sans-serif';
      ctx.fillStyle = '#991b1b';
      ctx.fillText('P&H SHOVEL #02', shovelX - 35, shovelY - 10);
      ctx.fillStyle = '#0f172a';
      ctx.font = '8px Inter, sans-serif';
      ctx.fillText('Active Face: 44.5% Mn', shovelX - 35, shovelY + 16);
      ctx.restore();

      // Drillhole markers if active layer
      if (activeLayer === 'drillholes' || activeLayer === 'all') {
        const drillholes = [
          { x: cx - 110, y: cy - 20, id: 'DH-01', depth: '185m', grade: '43.8%' },
          { x: cx + 70, y: cy + 10, id: 'DH-02', depth: '210m', grade: '41.2%' },
          { x: cx - 60, y: cy + 40, id: 'DH-03', depth: '165m', grade: '44.6%' }
        ];

        drillholes.forEach(dh => {
          // Drillhole core stem
          ctx.beginPath();
          ctx.moveTo(dh.x, dh.y);
          ctx.lineTo(dh.x, dh.y - 25);
          ctx.strokeStyle = '#8b5cf6';
          ctx.lineWidth = 2;
          ctx.stroke();

          // Collar head
          ctx.beginPath();
          ctx.arc(dh.x, dh.y - 25, 4, 0, Math.PI * 2);
          ctx.fillStyle = '#8b5cf6';
          ctx.fill();
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1;
          ctx.stroke();

          // Label
          ctx.font = '8px Inter, sans-serif';
          ctx.fillStyle = '#4c1d95';
          ctx.fillText(`${dh.id} (${dh.grade})`, dh.x + 6, dh.y - 23);
        });
      }

      if (autoRotate && !isDraggingRef.current) {
        setRotation(prev => ({ ...prev, y: (prev.y + 0.15) % 360 }));
      }

      animationFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [rotation, zoom, autoRotate, activeLayer]);

  // Mouse interaction handlers
  const handleMouseDown = (e) => {
    isDraggingRef.current = true;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e) => {
    if (!isDraggingRef.current) return;
    const dx = e.clientX - lastMousePosRef.current.x;
    const dy = e.clientY - lastMousePosRef.current.y;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };

    setRotation(prev => ({
      x: Math.max(20, Math.min(75, prev.x - dy * 0.3)),
      y: (prev.y + dx * 0.4) % 360
    }));
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  const handleWheel = (e) => {
    e.preventDefault();
    setZoom(prev => Math.max(0.7, Math.min(1.6, prev - e.deltaY * 0.001)));
  };

  return (
    <div className="mine-3d-container">
      {/* 3D Viewport Controls Bar */}
      <div className="viewer-toolbar">
        <div className="toolbar-left">
          <span className="live-telemetry-badge">
            <span className="pulse-dot"></span> 3D MINE PIT MODEL
          </span>
          <span className="mine-title-tag">{mineName}</span>
        </div>

        <div className="layer-selector-chips">
          <button 
            className={`chip-btn ${activeLayer === 'all' ? 'active' : ''}`}
            onClick={() => setActiveLayer('all')}
          >
            All Features
          </button>
          <button 
            className={`chip-btn ${activeLayer === 'ore' ? 'active' : ''}`}
            onClick={() => setActiveLayer('ore')}
          >
            Mn Ore Vein
          </button>
          <button 
            className={`chip-btn ${activeLayer === 'routes' ? 'active' : ''}`}
            onClick={() => setActiveLayer('routes')}
          >
            Haul Routes
          </button>
          <button 
            className={`chip-btn ${activeLayer === 'drillholes' ? 'active' : ''}`}
            onClick={() => setActiveLayer('drillholes')}
          >
            Drillhole Cores
          </button>
        </div>

        <div className="toolbar-right">
          <button 
            className={`tool-icon-btn ${autoRotate ? 'active' : ''}`}
            onClick={() => setAutoRotate(!autoRotate)}
            title={autoRotate ? "Pause Slow Orbit" : "Resume Slow Orbit"}
          >
            {autoRotate ? '⏸ Pause' : '▶ Orbit'}
          </button>
          <button 
            className="tool-icon-btn"
            onClick={() => setZoom(z => Math.min(1.6, z + 0.15))}
            title="Zoom In"
          >
            +
          </button>
          <button 
            className="tool-icon-btn"
            onClick={() => setZoom(z => Math.max(0.7, z - 0.15))}
            title="Zoom Out"
          >
            -
          </button>
          <button 
            className="tool-icon-btn"
            onClick={() => { setRotation({ x: 38, y: 45 }); setZoom(1); }}
            title="Reset Perspective"
          >
            ↺
          </button>
        </div>
      </div>

      {/* Main Interactive Canvas */}
      <div 
        className="canvas-wrapper"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      >
        <canvas ref={canvasRef} />

        {/* Floating Telemetry HUD */}
        <div className="telemetry-hud">
          <div className="hud-metric">
            <span className="hud-label">PIT ELEVATION</span>
            <span className="hud-val">+260m to +340m</span>
          </div>
          <div className="hud-metric">
            <span className="hud-label">ORE INTERCEPT</span>
            <span className="hud-val">14.2m Avg Thickness</span>
          </div>
          <div className="hud-metric">
            <span className="hud-label">CURRENT SHIFT ORE</span>
            <span className="hud-val">1,840 Tonnes Extracted</span>
          </div>
        </div>

        <div className="hint-overlay">
          <span>Click & drag to rotate pit camera • Scroll to zoom</span>
        </div>
      </div>
    </div>
  );
};

export default Mine3DViewer;
