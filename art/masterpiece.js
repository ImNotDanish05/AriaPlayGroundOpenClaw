const fs = require('fs');
const { createCanvas, loadImage } = require('canvas');
const path = require('path');
const axios = require('axios');

async function drawMasterpiece() {
    const width = 1920;
    const height = 1080;
    const canvas = createCanvas(width, height);
    const ctx = canvas.getContext('2d');

    // 1. ENVIRONMENT CONSTANTS
    const horizon = height * 0.65;
    const skyTextureUrl = 'https://dl.polyhaven.org/file/ph-assets/HDRIs/extra/Tonemapped%20JPG/golden_gate_hills.jpg';
    const sunPos = { x: 1600, y: 150, z: 2000 };

    // 2. PERSPECTIVE ENGINE (3D -> 2D)
    // Camera is at (0, 300, -800) looking towards positive Z
    const project = (x, y, z) => {
        const camZ = -800;
        const focalLength = 1000;
        const scale = focalLength / (z - camZ);
        return {
            x: (width / 2) + x * scale,
            y: horizon - y * scale,
            scale: scale
        };
    };

    // 3. SKY SPHERE SIMULATION
    try {
        const response = await axios({ url: skyTextureUrl, responseType: 'arraybuffer' });
        const skyImg = await loadImage(Buffer.from(response.data));
        
        // Draw sky sphere (background)
        ctx.save();
        // Create a slight curve for the horizon
        ctx.beginPath();
        ctx.rect(0, 0, width, horizon + 50);
        ctx.clip();
        
        // Perspective warp simulation for the sky background
        ctx.drawImage(skyImg, 0, 0, width, horizon + 100);
        
        // Atmosphere haze
        const haze = ctx.createLinearGradient(0, horizon - 200, 0, horizon);
        haze.addColorStop(0, 'rgba(255, 255, 255, 0)');
        haze.addColorStop(1, 'rgba(255, 220, 180, 0.4)');
        ctx.fillStyle = haze;
        ctx.fillRect(0, 0, width, horizon);
        ctx.restore();
    } catch (e) {
        ctx.fillStyle = '#87CEEB';
        ctx.fillRect(0, 0, width, horizon);
    }

    // 4. GROUND (Grass with depth)
    const grassGrad = ctx.createLinearGradient(0, horizon, 0, height);
    grassGrad.addColorStop(0, '#2d4a10');
    grassGrad.addColorStop(1, '#1a2e05');
    ctx.fillStyle = grassGrad;
    ctx.fillRect(0, horizon, width, height - horizon);

    // 5. ASPHALT ROAD (3D Perspective)
    const roadWidth = 250;
    const r1 = project(-roadWidth, 0, 0);
    const r2 = project(roadWidth, 0, 0);
    const r3 = project(roadWidth * 5, 0, 5000); // Deep into horizon
    const r4 = project(-roadWidth * 5, 0, 5000);

    ctx.fillStyle = '#1e293b';
    ctx.beginPath();
    ctx.moveTo(r1.x, r1.y); ctx.lineTo(r2.x, r2.y);
    ctx.lineTo(r3.x, r3.y); ctx.lineTo(r4.x, r4.y);
    ctx.closePath();
    ctx.fill();

    // Road dashed lines
    ctx.strokeStyle = '#f8fafc';
    ctx.setLineDash([40, 60]);
    ctx.lineWidth = 5;
    ctx.beginPath();
    const rl1 = project(0, 0, 0);
    const rl2 = project(0, 0, 5000);
    ctx.moveTo(rl1.x, rl1.y); ctx.lineTo(rl2.x, rl2.y);
    ctx.stroke();
    ctx.setLineDash([]);

    // 6. SHADOW GENERATOR
    const castShadow = (points) => {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.45)';
        ctx.beginPath();
        points.forEach((p, i) => {
            // Shadow projection towards ground
            const dx = p.x - sunPos.x;
            const dy = p.y - sunPos.y;
            const shadowX = p.x + (dx * (p.y / sunPos.y + 0.5));
            const shadowY = horizon; // Projected on ground plane
            if (i === 0) ctx.moveTo(shadowX, shadowY + 20);
            else ctx.lineTo(shadowX, shadowY + 20);
        });
        ctx.closePath();
        ctx.fill();
    };

    // 7. TREE (Built with Spheres)
    const treeZ = 600;
    const treeX = -450;
    const tBase = project(treeX, 0, treeZ);
    
    // Shadow Tree
    ctx.fillStyle = 'rgba(0,0,0,0.35)';
    ctx.beginPath();
    ctx.ellipse(tBase.x + 150, tBase.y + 10, 150 * tBase.scale, 40 * tBase.scale, 0, 0, Math.PI * 2);
    ctx.fill();

    // Trunk
    ctx.fillStyle = '#451a03';
    const trunkW = 40 * tBase.scale;
    const trunkH = 200 * tBase.scale;
    ctx.fillRect(tBase.x - trunkW/2, tBase.y - trunkH, trunkW, trunkH);

    // Leaves (Recursive Spheres)
    const drawLeaf = (lx, ly, lz, r) => {
        const p = project(lx, ly, lz);
        const rad = r * p.scale;
        const g = ctx.createRadialGradient(p.x - rad*0.3, p.y - rad*0.3, rad*0.1, p.x, p.y, rad);
        g.addColorStop(0, '#4ade80');
        g.addColorStop(1, '#064e3b');
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(p.x, p.y, rad, 0, Math.PI * 2); ctx.fill();
    };
    drawLeaf(treeX, 250, treeZ, 120);
    drawLeaf(treeX - 70, 180, treeZ + 50, 90);
    drawLeaf(treeX + 70, 180, treeZ - 50, 90);
    drawLeaf(treeX, 350, treeZ, 80);

    // 8. THE HOUSE (Precise 3D Geometry)
    const hX = 200, hY = 0, hZ = 800;
    const hW = 450, hH = 350, hD = 400;

    // Corner points
    const p = [
        project(hX, hY, hZ),          // 0: front bottom left
        project(hX+hW, hY, hZ),       // 1: front bottom right
        project(hX+hW, hY+hH, hZ),    // 2: front top right
        project(hX, hY+hH, hZ),       // 3: front top left
        project(hX, hY, hZ+hD),       // 4: back bottom left
        project(hX+hW, hY, hZ+hD),    // 5: back bottom right
        project(hX+hW, hY+hH, hZ+hD), // 6: back top right
        project(hX, hY+hH, hZ+hD)     // 7: back top left
    ];

    // House Shadow
    castShadow([p[0], p[1], p[5], p[4]]);

    // Walls (Sorted by depth)
    // Side wall (shaded)
    ctx.fillStyle = '#fde68a';
    ctx.beginPath(); ctx.moveTo(p[1].x, p[1].y); ctx.lineTo(p[5].x, p[5].y); ctx.lineTo(p[6].x, p[6].y); ctx.lineTo(p[2].x, p[2].y); ctx.fill();
    // Front wall (lit)
    ctx.fillStyle = '#fef3c7';
    ctx.beginPath(); ctx.moveTo(p[0].x, p[0].y); ctx.lineTo(p[1].x, p[1].y); ctx.lineTo(p[2].x, p[2].y); ctx.lineTo(p[3].x, p[3].y); ctx.fill();
    ctx.strokeStyle = '#d97706'; ctx.lineWidth = 1; ctx.stroke();

    // ROOF (Gable/Pyramid)
    const peak = project(hX + hW/2, hH + 200, hZ + hD/2);
    // Roof sides
    ctx.fillStyle = '#7f1d1d'; // Side
    ctx.beginPath(); ctx.moveTo(p[2].x, p[2].y); ctx.lineTo(p[6].x, p[6].y); ctx.lineTo(peak.x, peak.y); ctx.fill();
    ctx.fillStyle = '#b91c1c'; // Front
    ctx.beginPath(); ctx.moveTo(p[3].x, p[3].y); ctx.lineTo(p[2].x, p[2].y); ctx.lineTo(peak.x, peak.y); ctx.fill();
    ctx.stroke();

    // DOOR
    const dw = 80, dh = 150;
    const d1 = project(hX + 185, 0, hZ);
    const d2 = project(hX + 185 + dw, 0, hZ);
    const d3 = project(hX + 185 + dw, dh, hZ);
    const d4 = project(hX + 185, dh, hZ);
    ctx.fillStyle = '#451a03';
    ctx.beginPath(); ctx.moveTo(d1.x, d1.y); ctx.lineTo(d2.x, d2.y); ctx.lineTo(d3.x, d3.y); ctx.lineTo(d4.x, d4.y); ctx.fill();

    // WINDOWS
    const drawWindow3D = (x, y) => {
        const w1 = project(x, y, hZ);
        const w2 = project(x+70, y, hZ);
        const w3 = project(x+70, y+70, hZ);
        const w4 = project(x, y+70, hZ);
        ctx.fillStyle = '#bae6fd';
        ctx.beginPath(); ctx.moveTo(w1.x, w1.y); ctx.lineTo(w2.x, w2.y); ctx.lineTo(w3.x, w3.y); ctx.lineTo(w4.x, w4.y); ctx.fill();
        ctx.strokeStyle = '#0284c7'; ctx.stroke();
    };
    drawWindow3D(hX + 50, 150);
    drawWindow3D(hX + 330, 150);

    // 9. THE SUN (Bright Sphere)
    const sunScreen = { x: 1600, y: 150 };
    const sunGlow = ctx.createRadialGradient(sunScreen.x, sunScreen.y, 20, sunScreen.x, sunScreen.y, 150);
    sunGlow.addColorStop(0, 'rgba(255, 255, 200, 1)');
    sunGlow.addColorStop(0.2, 'rgba(255, 255, 0, 0.6)');
    sunGlow.addColorStop(1, 'rgba(255, 255, 255, 0)');
    ctx.fillStyle = sunGlow;
    ctx.fillRect(0, 0, width, height);

    // 10. SAVE MASTERPIECE
    const buffer = canvas.toBuffer('image/png');
    const finalPath = '/home/claw/.openclaw/workspace/art/house_3d_final.png';
    fs.writeFileSync(finalPath, buffer);
    console.log("Masterpiece saved to " + finalPath);
}

drawMasterpiece();
