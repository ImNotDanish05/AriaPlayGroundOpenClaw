import math
import random
import numpy as np
import time
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

def render_space_scene():
    width, height = 1000, 1000
    # 1. Background: Deep Space with Stars
    img = Image.new("RGB", (width, height), (5, 5, 15))
    draw = ImageDraw.Draw(img)
    
    # Procedural Stars
    for _ in range(400):
        x, y = random.randint(0, width), random.randint(0, height)
        size = random.choice([1, 1, 2])
        brightness = random.randint(150, 255)
        draw.point((x, y), fill=(brightness, brightness, brightness))

    pixels = img.load()

    # 2. Distant Sun Glow (Top Left)
    sun_pos = [150, 150]
    for r in range(250, 0, -5):
        alpha = int(100 * (1 - r/250))
        # Add additive glow manually or via ellipse
        draw.ellipse([sun_pos[0]-r, sun_pos[1]-r, sun_pos[0]+r, sun_pos[1]+r], 
                     fill=(255, 255, 200 + alpha//2), outline=None)

    # 3. Raycasting Earth and Moon
    # Earth: center (500, 600, -300), radius 200
    # Moon: center (800, 300, -100), radius 40
    
    light_dir = np.array([-1.0, -1.0, 1.0]) # From sun
    light_dir = light_dir / np.linalg.norm(light_dir)

    def get_color(x, y, center, r, type="earth"):
        dx, dy = x - center[0], y - center[1]
        disc = r**2 - (dx**2 + dy**2)
        if disc < 0: return None
        
        dz = math.sqrt(disc)
        z = center[2] + dz
        
        # Normal
        nx, ny, nz = dx/r, dy/r, dz/r
        
        # Shading
        dot = max(0.05, nx*light_dir[0] + ny*light_dir[1] + nz*light_dir[2])
        
        if type == "earth":
            # Procedural Earth Texture (Blue/Green/White)
            noise_val = (math.sin(x/30 + z/20) * math.cos(y/30))
            if noise_val > 0.4: color = (34, 139, 34) # Green Land
            elif noise_val > 0.2: color = (255, 255, 255) # White Clouds
            else: color = (30, 60, 180) # Blue Ocean
        else:
            # Moon Texture (Grey)
            color = (180, 180, 185)
            
        return tuple(int(c * dot) for c in color)

    print("Rendering celestial bodies...")
    for py in range(height):
        for px in range(width):
            # Check Moon first (closer to camera in Z)
            m_color = get_color(px, py, [800, 300, -100], 45, "moon")
            if m_color:
                pixels[px, py] = m_color
                continue
            
            # Check Earth
            e_color = get_color(px, py, [500, 600, -300], 250, "earth")
            if e_color:
                pixels[px, py] = e_color

    # 4. Post Processing
    # Blur a bit for glow effect
    img = img.filter(ImageFilter.SMOOTH)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.4)
    
    timestamp = int(time.time())
    path = f"/home/claw/.openclaw/workspace/procedural_earth_{timestamp}.png"
    img.save(path)
    print(f"MEDIA:{path}")

if __name__ == "__main__":
    render_space_scene()
