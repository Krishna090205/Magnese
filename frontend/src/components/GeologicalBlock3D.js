import React, { useRef, useEffect, useState } from 'react';

const GeologicalBlock3D = ({ blockData, depthSlice = 180, onDepthChange }) => {
  const canvasRef = useRef(null);
  const [rotation, setRotation] = useState({ x: 32, y: -35 });
  const [currentDepth, setCurrentDepth] = useState(depthSlice);
  const isDraggingRef = useRef(false);
  const lastMousePosRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = (canvas.width = canvas.parentElement.clientWidth || 700);
    const height = (canvas.height = canvas.parentElement.clientHeight || 420);

    const cx = width / 2;
    const cy = height / 2 + 10;

    const blockSize = 32;

    const radX = (rotation.x * Math.PI) / 180;
    const radY = (rotation.y * Math.PI) / 180;

    // Render loop
    ctx.clearRect(0, 0, width, height);

    // Subtle background
    const bgGrad = ctx.createLinearGradient(0, 0, 0, height);
    bgGrad.addColorStop(0, '#f8fafc');
    bgGrad.addColorStop(1, '#edf2f7');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, width, height);

    // Subterranean coordinate grid
    ctx.save();
    ctx.strokeStyle = 'rgba(203, 213, 225, 0.5)';
    ctx.lineWidth = 1;
    ctx.strokeRect(30, 30, width - 60, height - 60);
    ctx.restore();

    // Sort voxels back-to-front (Painter's algorithm)
    const blocks = [];
    for (let gx = -2; gx <= 2; gx++) {
      for (let gy = 0; gy < 4; gy++) {
        for (let gz = -2; gz <= 2; gz++) {
          const depthM = (gy + 1) * 60;
          if (depthM > currentDepth + 30) continue; // Cutaway slider filter

          // Grade calculation based on depth and position (concentrated in center core)
          const distFromCore = Math.sqrt(gx * gx + gz * gz);
          let mnGrade = 44.5 - distFromCore * 5.2 - gy * 1.5;
          if (mnGrade < 18) mnGrade = 18 + Math.random() * 4;

          // 3D coordinates
          const posX = gx * (blockSize + 6);
          const posY = gy * (blockSize + 6) - 50;
          const posZ = gz * (blockSize + 6);

          // Rotate Y
          const rotX1 = posX * Math.cos(radY) + posZ * Math.sin(radY);
          const rotZ1 = -posX * Math.sin(radY) + posZ * Math.cos(radY);

          // Rotate X
          const rotY2 = posY * Math.cos(radX) - rotZ1 * Math.sin(radX);
          const rotZ2 = posY * Math.sin(radX) + rotZ1 * Math.cos(radX);

          // Isometric project
          const projX = cx + rotX1;
          const projY = cy + rotY2;

          blocks.push({
            gx, gy, gz,
            projX, projY,
            depthZ: rotZ2,
            mnGrade,
            depthM,
            density: 3.4 + (mnGrade / 100) * 0.8
          });
        }
      }
    }

    // Sort by depth (farthest first)
    blocks.sort((a, b) => b.depthZ - a.depthZ);

    // Color mapper
    const getBlockColor = (grade) => {
      if (grade >= 42) return { top: '#4338ca', side1: '#3730a3', side2: '#312e81' }; // High Grade Deep Indigo
      if (grade >= 35) return { top: '#2563eb', side1: '#1d4ed8', side2: '#1e40af' }; // Med-High Cobalt
      if (grade >= 26) return { top: '#0284c7', side1: '#0369a1', side2: '#075985' }; // Medium Cyan-Blue
      return { top: '#94a3b8', side1: '#64748b', side2: '#475569' }; // Waste / Overburden
    };

    // Draw blocks
    const s = blockSize / 2;
    blocks.forEach((b) => {
      const colors = getBlockColor(b.mnGrade);

      // Top face
      ctx.beginPath();
      ctx.moveTo(b.projX, b.projY - s);
      ctx.lineTo(b.projX + s, b.projY - s / 2);
      ctx.lineTo(b.projX, b.projY);
      ctx.lineTo(b.projX - s, b.projY - s / 2);
      ctx.closePath();
      ctx.fillStyle = colors.top;
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 0.8;
      ctx.stroke();

      // Left face
      ctx.beginPath();
      ctx.moveTo(b.projX - s, b.projY - s / 2);
      ctx.lineTo(b.projX, b.projY);
      ctx.lineTo(b.projX, b.projY + s);
      ctx.lineTo(b.projX - s, b.projY + s / 2);
      ctx.closePath();
      ctx.fillStyle = colors.side1;
      ctx.fill();
      ctx.stroke();

      // Right face
      ctx.beginPath();
      ctx.moveTo(b.projX, b.projY);
      ctx.lineTo(b.projX + s, b.projY - s / 2);
      ctx.lineTo(b.projX + s, b.projY + s / 2);
      ctx.lineTo(b.projX, b.projY + s);
      ctx.closePath();
      ctx.fillStyle = colors.side2;
      ctx.fill();
      ctx.stroke();
    });

  }, [rotation, currentDepth]);

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
      x: Math.max(15, Math.min(65, prev.x - dy * 0.3)),
      y: (prev.y + dx * 0.4) % 360
    }));
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  return (
    <div className="geological-block-3d-card">
      <div className="card-header-clean">
        <div>
          <h4>3D Subsurface Ore Block Voxel Model</h4>
          <span className="subtext">Stratigraphic Mn grade distribution & UNFC reserve block model</span>
        </div>
        <div className="block-controls-inline">
          <div className="depth-slider-group">
            <label>Cutaway Depth: <strong>-{currentDepth}m</strong></label>
            <input 
              type="range" 
              min="60" 
              max="240" 
              step="30"
              value={currentDepth}
              onChange={(e) => {
                const val = parseInt(e.target.value);
                setCurrentDepth(val);
                if (onDepthChange) onDepthChange(val);
              }}
            />
          </div>
          <button 
            className="tool-icon-btn"
            onClick={() => setRotation({ x: 32, y: -35 })}
            title="Reset Perspective"
          >
            ↺ Reset Angle
          </button>
        </div>
      </div>

      <div 
        className="block-canvas-container"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <canvas ref={canvasRef} />

        {/* Grade Color Legend */}
        <div className="grade-legend-bar">
          <div className="legend-label-title">Mn Grade %</div>
          <div className="legend-items">
            <span className="legend-chip high">● &gt;42% High Grade (Pyrolusite/Braunite)</span>
            <span className="legend-chip med">● 35–42% Medium Grade</span>
            <span className="legend-chip low">● 26–35% Low Grade</span>
            <span className="legend-chip waste">● Overburden / Schist Host</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeologicalBlock3D;
