import React, { useRef, useEffect, useState } from 'react';

const FleetRoute3D = ({ trucks = [], onSelectTruck }) => {
  const canvasRef = useRef(null);
  const selectedTruckId = null;
  const [simSpeed, setSimSpeed] = useState(1);
  const animationFrameRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = (canvas.width = canvas.parentElement.clientWidth || 800);
    const height = (canvas.height = canvas.parentElement.clientHeight || 420);

    // Fleet trucks with dynamic progress along route
    const fleet = [
      { id: 'HT-01', model: 'Komatsu HD785-7', progress: 0.15, speed: 0.002, status: 'Hauling Loaded', payload: '98.4 T', source: 'Bench +280m', dest: 'Crusher #1' },
      { id: 'HT-02', model: 'Komatsu HD785-7', progress: 0.38, speed: 0.0018, status: 'Dumping Ore', payload: '96.2 T', source: 'Bench +260m', dest: 'Crusher #1' },
      { id: 'HT-03', model: 'CAT 777E', progress: 0.58, speed: 0.0026, status: 'Returning Empty', payload: '0 T', source: 'Crusher #1', dest: 'Shovel Face #02' },
      { id: 'HT-04', model: 'CAT 777E', progress: 0.76, speed: 0.0021, status: 'Loading Face', payload: '62.0 T', source: 'Bench +280m', dest: 'Stockpile Alpha' },
      { id: 'HT-05', model: 'BEML BH100', progress: 0.92, speed: 0.0024, status: 'Hauling Loaded', payload: '101.5 T', source: 'Bench +300m', dest: 'Crusher #2' },
    ];

    // Route waypoint path coordinates (2.5D Isometric Mine Ramp)
    const waypoints = [
      { x: 120, y: 340, name: 'Bench +260m Face', elev: '+260m' },
      { x: 260, y: 310, name: 'Bench +280m Switchback', elev: '+280m' },
      { x: 380, y: 240, name: 'Main Pit Ramp Rampway', elev: '+300m' },
      { x: 520, y: 160, name: 'Upper Rim Junction', elev: '+320m' },
      { x: 680, y: 110, name: 'Primary Gyratory Crusher', elev: '+340m' }
    ];

    const getPointOnPath = (t) => {
      // Loop from 0 to 1 along waypoint polyline
      const totalSegments = waypoints.length - 1;
      const segIndex = Math.min(Math.floor(t * totalSegments), totalSegments - 1);
      const segT = (t * totalSegments) - segIndex;
      const p1 = waypoints[segIndex];
      const p2 = waypoints[segIndex + 1];

      return {
        x: p1.x + (p2.x - p1.x) * segT,
        y: p1.y + (p2.y - p1.y) * segT,
        elev: p1.elev
      };
    };

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Soft light gradient background
      const bgGrad = ctx.createLinearGradient(0, 0, 0, height);
      bgGrad.addColorStop(0, '#f8fafc');
      bgGrad.addColorStop(1, '#edf2f7');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Draw Mine Topography Contour Ridges in soft slate
      ctx.save();
      ctx.strokeStyle = 'rgba(203, 213, 225, 0.6)';
      ctx.lineWidth = 1;
      for (let c = 0; c < 5; c++) {
        ctx.beginPath();
        ctx.ellipse(380, 240 + c * 25, 340 + c * 20, 160 + c * 10, -0.2, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.restore();

      // Draw Haulage Road Asphalt Ribbon
      ctx.save();
      ctx.beginPath();
      waypoints.forEach((wp, idx) => {
        if (idx === 0) ctx.moveTo(wp.x, wp.y);
        else ctx.lineTo(wp.x, wp.y);
      });
      ctx.strokeStyle = '#94a3b8';
      ctx.lineWidth = 24;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.stroke();

      // Road Inner Centerline
      ctx.beginPath();
      waypoints.forEach((wp, idx) => {
        if (idx === 0) ctx.moveTo(wp.x, wp.y);
        else ctx.lineTo(wp.x, wp.y);
      });
      ctx.strokeStyle = '#e2e8f0';
      ctx.lineWidth = 2;
      ctx.setLineDash([8, 6]);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.restore();

      // Draw Key Stations along Route
      waypoints.forEach((wp, idx) => {
        // Station node
        ctx.beginPath();
        ctx.arc(wp.x, wp.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = idx === 0 ? '#3b82f6' : (idx === waypoints.length - 1 ? '#0f2b5c' : '#ffffff');
        ctx.fill();
        ctx.strokeStyle = '#0f2b5c';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Station label card
        ctx.save();
        ctx.font = 'bold 10px Inter, sans-serif';
        ctx.fillStyle = '#0f172a';
        ctx.fillText(wp.name, wp.x - 20, wp.y - 14);
        ctx.font = '9px Inter, sans-serif';
        ctx.fillStyle = '#64748b';
        ctx.fillText(`Elev: ${wp.elev}`, wp.x - 20, wp.y + 20);
        ctx.restore();
      });

      // Update and Draw Trucks
      fleet.forEach((truck) => {
        truck.progress = (truck.progress + truck.speed * simSpeed) % 1;
        const pos = getPointOnPath(truck.progress);

        const isSelected = selectedTruckId === truck.id;
        const isLoaded = truck.payload !== '0 T';

        // Truck shadow
        ctx.beginPath();
        ctx.ellipse(pos.x, pos.y + 4, 12, 5, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(15, 23, 42, 0.2)';
        ctx.fill();

        // Truck Dumper Body
        ctx.save();
        ctx.beginPath();
        ctx.roundRect(pos.x - 9, pos.y - 8, 18, 14, 3);
        ctx.fillStyle = isSelected ? '#2563eb' : (isLoaded ? '#1e3a8a' : '#d97706');
        ctx.fill();
        ctx.strokeStyle = isSelected ? '#60a5fa' : '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Truck Cab
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(pos.x + 2, pos.y - 6, 6, 6);

        // Status Tag Flag
        ctx.font = 'bold 9px Inter, sans-serif';
        ctx.fillStyle = '#0f172a';
        ctx.fillText(truck.id, pos.x + 12, pos.y - 4);
        ctx.font = '8px Inter, sans-serif';
        ctx.fillStyle = isLoaded ? '#1d4ed8' : '#b45309';
        ctx.fillText(`${truck.status} (${truck.payload})`, pos.x + 12, pos.y + 6);
        ctx.restore();
      });

      animationFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [simSpeed, selectedTruckId]);

  return (
    <div className="fleet-route-3d-card">
      <div className="route-header-clean">
        <div>
          <h4>2.5D Mine Pit Haulage Route Network</h4>
          <span className="subtext">Real-time dumper dispatch between active bench faces and gyratory crusher</span>
        </div>
        <div className="route-actions-inline">
          <button 
            className={`pill-toggle-btn ${simSpeed === 1 ? 'active' : ''}`}
            onClick={() => setSimSpeed(1)}
          >
            1x Live
          </button>
          <button 
            className={`pill-toggle-btn ${simSpeed === 2 ? 'active' : ''}`}
            onClick={() => setSimSpeed(2)}
          >
            2x Sim
          </button>
          <button 
            className={`pill-toggle-btn ${simSpeed === 0 ? 'active' : ''}`}
            onClick={() => setSimSpeed(s => s === 0 ? 1 : 0)}
          >
            {simSpeed === 0 ? 'Resume' : 'Pause'}
          </button>
        </div>
      </div>

      <div className="route-canvas-wrapper">
        <canvas ref={canvasRef} />

        {/* Floating Route Gradient Telemetry */}
        <div className="route-specs-badge">
          <div className="spec-row">
            <span className="spec-label">RAMP GRADIENT:</span>
            <span className="spec-val">7.8% Avg (Permissible: &le; 10%)</span>
          </div>
          <div className="spec-row">
            <span className="spec-label">ONE-WAY DISTANCE:</span>
            <span className="spec-val">1.65 km Bench to Crusher</span>
          </div>
          <div className="spec-row">
            <span className="spec-label">ROAD CONDITION:</span>
            <span className="spec-val text-green">Dry & Compacted • Grade A</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FleetRoute3D;
