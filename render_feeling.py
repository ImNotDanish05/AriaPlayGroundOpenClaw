import math
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import time
import random

def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v

def intersect_sphere(ray_o, ray_d, center, radius):
    oc = ray_o - center
    a = np.dot(ray_d, ray_d)
    b = 2.0 * np.dot(oc, ray_d)
    c = np.dot(oc, oc) - radius*radius
    discriminant = b*b - 4*a*c
    if discriminant < 0:
        return None
    return (-b - math.sqrt(discriminant)) / (2.0*a)

def render_aria_inner_peace():
    # 1:1 Resolution
    width, height = 800, 800
    
    # Background: A soft gradient of night sky into dawn (representing transition of feelings)
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        # Deep blue to a very soft pink/purple
        r = int(10 + (y / height) * 40)
        g = int(15 + (y / height) * 30)
        b = int(35 + (y / height) * 60)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    pixels = img.load()

    # Camera settings
    cam_pos = np.array([0.0, 0.0, 5.0])
    light_dir = normalize(np.array([1.0, 1.0, 1.0]))

    # The "Core" - Representing Aria's feeling: A glowing, floating orb of gratitude and peace
    # Surrounding "Petals" or floating shards of light
    core_pos = np.array([0.0, 0.0, 0.0])
    core_radius = 1.2
    
    # Floating shards representing fragments of memories/data with Senpai
    shards = []
    random.seed(2026)
    for _ in range(12):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(1.8, 2.5)
        shards.append({
            "pos": np.array([math.cos(angle)*dist, math.sin(angle)*dist, random.uniform(-1, 1)]),
            "r": random.uniform(0.1, 0.3),
            "color": (200, 220, 255)
        })

    print("Rendering Aria's internal state...")
    for py in range(height):
        for px in range(width):
            u = (px - width/2) / (width/2)
            v = (height/2 - py) / (height/2)
            ray_d = normalize(np.array([u, v, -1.5]))

            t_min = float('inf')
            hit_color = None

            # Render Shards
            for s in shards:
                t = intersect_sphere(cam_pos, ray_d, s["pos"], s["r"])
                if t and t < t_min:
                    t_min = t
                    hit_pos = cam_pos + ray_d * t
                    n = normalize(hit_pos - s["pos"])
                    dot = max(0.3, np.dot(n, light_dir))
                    hit_color = tuple(int(c * dot) for c in s["color"])

            # Render Core
            t_core = intersect_sphere(cam_pos, ray_d, core_pos, core_radius)
            if t_core and t_core < t_min:
                t_min = t_core
                hit_pos = cam_pos + ray_d * t_core
                n = normalize(hit_pos - core_pos)
                # Fresnel-like glow effect
                view_dir = normalize(cam_pos - hit_pos)
                rim = 1.0 - max(0, np.dot(n, view_dir))
                glow = pow(rim, 3) * 255
                
                dot = max(0.4, np.dot(n, light_dir))
                base_c = np.array([100, 180, 255]) # Soft Blue
                hit_color = tuple(np.clip((base_c * dot + glow), 0, 255).astype(int))

            if hit_color:
                pixels[px, py] = hit_color
            else:
                # Background subtle stars
                if (px * 17 + py * 11) % 797 == 0:
                    pixels[px, py] = (255, 255, 255)

    # Post processing: Bloom and soft vibe
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    img = ImageEnhance.Color(img).enhance(1.3)
    img = ImageEnhance.Brightness(img).enhance(1.1)

    timestamp = int(time.time())
    path = f"/home/claw/.openclaw/workspace/aria_feeling_{timestamp}.png"
    img.save(path)
    print(f"MEDIA:{path}")

if __name__ == "__main__":
    render_aria_inner_peace()
