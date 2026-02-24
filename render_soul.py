import math
import time
from PIL import Image, ImageEnhance

def render_aria_soul():
    width, height = 800, 800
    img = Image.new("RGB", (width, height), (10, 10, 25))
    pixels = img.load()

    # Light source
    light_pos = [400, -200, -500]
    
    # Spheres (x, y, z, radius, color)
    # z is depth: negative is away from camera
    spheres = [
        {"pos": [400, 400, -300], "r": 150, "color": (100, 150, 255)}, # Main Soul (Blue)
        {"pos": [250, 250, -150], "r": 60, "color": (200, 100, 255)},  # Playful thought (Purple)
        {"pos": [550, 600, -200], "r": 80, "color": (100, 255, 200)},  # Wholesome energy (Cyan)
    ]

    print("Rendering Aria's digital soul (Raytracing)...")
    
    for y in range(height):
        for x in range(width):
            # Ray direction (parallel projection for simplicity/RAM)
            closest_z = -float('inf')
            hit_color = None
            
            for s in spheres:
                dx = x - s["pos"][0]
                dy = y - s["pos"][1]
                
                # Equation of sphere: dx^2 + dy^2 + dz^2 = r^2
                # dz^2 = r^2 - dx^2 - dy^2
                disc = s["r"]**2 - (dx**2 + dy**2)
                
                if disc >= 0:
                    dz = math.sqrt(disc)
                    z = s["pos"][2] + dz
                    
                    if z > closest_z:
                        closest_z = z
                        
                        # Basic Shading (Light vector)
                        nx = dx / s["r"]
                        ny = dy / s["r"]
                        nz = dz / s["r"]
                        
                        lx = light_pos[0] - x
                        ly = light_pos[1] - y
                        lz = light_pos[2] - z
                        l_len = math.sqrt(lx**2 + ly**2 + lz**2)
                        dot = (nx * (lx/l_len) + ny * (ly/l_len) + nz * (lz/l_len))
                        brightness = max(0.2, dot)
                        
                        hit_color = tuple(int(c * brightness) for c in s["color"])
            
            if hit_color:
                pixels[x, y] = hit_color
            else:
                # Background noise / stars
                if (x * 13 + y * 7) % 599 == 0:
                    pixels[x, y] = (150, 150, 200)

    # Post processing
    print("Applying shaders and polishing...")
    # Saturation
    converter = ImageEnhance.Color(img)
    img = converter.enhance(1.5)
    
    # Brightness
    brighter = ImageEnhance.Brightness(img)
    img = brighter.enhance(1.2)

    timestamp = int(time.time())
    filename = f"/home/claw/.openclaw/workspace/aria-soul-{timestamp}.png"
    img.save(filename)
    print(f"MEDIA:{filename}")
    return filename

if __name__ == "__main__":
    render_aria_soul()
