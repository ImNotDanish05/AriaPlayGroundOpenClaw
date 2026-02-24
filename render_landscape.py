import math
import random
import numpy as np
import time
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

def generate_noise(w, h, scale=10.0, octaves=4):
    """Simple procedural fractal noise generator (simplified Perlin-ish)"""
    noise = np.zeros((h, w))
    for o in range(octaves):
        freq = 2**o
        amp = 0.5**o
        # Generate random grid for this octave
        rw, rh = int(w/scale * freq) + 2, int(h/scale * freq) + 2
        grid = np.random.rand(rh, rw)
        
        # Interpolate
        for y in range(h):
            for x in range(w):
                gx, gy = x/w * (rw-1), y/h * (rh-1)
                ix, iy = int(gx), int(gy)
                fx, fy = gx - ix, gy - iy
                
                # Bi-linear interpolation
                v1 = grid[iy, ix]
                v2 = grid[iy, ix+1]
                v3 = grid[iy+1, ix]
                v4 = grid[iy+1, ix+1]
                
                # Smoothstep
                sx = fx * fx * (3 - 2 * fx)
                sy = fy * fy * (3 - 2 * fy)
                
                interp = v1*(1-sx)*(1-sy) + v2*sx*(1-sy) + v3*(1-sx)*sy + v4*sx*sy
                noise[y, x] += interp * amp
                
    return noise / (2.0 - 0.5**(octaves-1))

def render_mountain_landscape():
    width, height = 1200, 800
    # 1. Sky Gradient (Sunset/Dawn Vibe)
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        # Blend from deep blue to orange/pink
        r = int(20 + (y / height) * 200)
        g = int(30 + (y / height) * 100)
        b = int(60 + (y / height) * 50)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Draw a glowing Sun
    sun_x, sun_y = 900, 250
    for r in range(120, 0, -2):
        alpha = int(255 * (1 - r/120))
        # Simulated glow
        draw.ellipse([sun_x-r, sun_y-r, sun_x+r, sun_y+r], 
                     fill=(255, 230, 150), outline=None)

    # 3. Generate Landscape Data
    grid_size = 300
    noise = generate_noise(grid_size, grid_size, scale=5.0, octaves=5)
    
    # Projection parameters
    cam_pos = [grid_size/2, 50, grid_size + 100]
    look_at = [grid_size/2, 0, 0]
    light_dir = np.array([1.0, 1.0, 1.0])
    light_dir = light_dir / np.linalg.norm(light_dir)

    def project_3d(x, y, z):
        # Simple perspective
        # Translate relative to camera
        tx, ty, tz = x - cam_pos[0], y - cam_pos[1], z - cam_pos[2]
        # Tilt camera down slightly
        angle = -0.3
        ny = ty * math.cos(angle) - tz * math.sin(angle)
        nz = ty * math.sin(angle) + tz * math.cos(angle)
        
        scale = 800 / (max(1, nz + 400))
        px = tx * scale + width / 2
        py = -ny * scale + height / 2 + 100
        return (px, py), nz

    # 4. Draw Polygons (Back to Front)
    print("Computing polygons...")
    polygons = []
    for z in range(grid_size - 1):
        for x in range(grid_size - 1):
            h1 = noise[z, x] * 120
            h2 = noise[z, x+1] * 120
            h3 = noise[z+1, x+1] * 120
            h4 = noise[z+1, x] * 120
            
            p1, d1 = project_3d(x, h1, z)
            p2, d2 = project_3d(x+1, h2, z)
            p3, d3 = project_3d(x+1, h3, z+1)
            p4, d4 = project_3d(x, h4, z+1)
            
            # Simple color based on height
            avg_h = (h1+h2+h3+h4)/4
            if avg_h > 80: color = (255, 255, 255) # Snow
            elif avg_h > 50: color = (100, 110, 120) # Rock
            else: color = (34, 100, 34) # Forest
            
            # Shading
            # Calculate normal roughly
            v1 = np.array([1, h2-h1, 0])
            v2 = np.array([0, h4-h1, 1])
            normal = np.cross(v1, v2)
            norm_len = np.linalg.norm(normal)
            if norm_len > 0:
                normal = normal / norm_len
                dot = np.dot(normal, light_dir)
                brightness = max(0.3, dot)
            else:
                brightness = 0.5
            
            # Distance fog (blend to sky/atmosphere)
            fog = max(0, min(1, (d1 + 100) / 400))
            final_color = tuple(int(c * brightness * (1-fog) + 150 * fog) for c in color)
            
            polygons.append({
                "pts": [p1, p2, p3, p4],
                "depth": d1 + d2 + d3 + d4,
                "color": final_color
            })

    # Sort polygons by depth (Back to Front)
    polygons.sort(key=lambda x: x["depth"], reverse=True)
    
    print("Drawing mountains...")
    for poly in polygons:
        # Only draw if on screen
        if all(0 <= pt[0] <= width and 0 <= pt[1] <= height for pt in poly["pts"]):
            draw.polygon(poly["pts"], fill=poly["color"])

    # 5. Post Processing
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.4)

    timestamp = int(time.time())
    path = f"/home/claw/.openclaw/workspace/procedural_mountain_{timestamp}.png"
    img.save(path)
    print(f"MEDIA:{path}")

if __name__ == "__main__":
    render_mountain_landscape()
