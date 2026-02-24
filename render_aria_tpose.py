import math
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import time

def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v

def intersect_aabb(ray_o, ray_d, box_min, box_max):
    t_near = -float('inf')
    t_far = float('inf')
    for i in range(3):
        if abs(ray_d[i]) < 1e-6:
            if ray_o[i] < box_min[i] or ray_o[i] > box_max[i]:
                return None
        else:
            t1 = (box_min[i] - ray_o[i]) / ray_d[i]
            t2 = (box_max[i] - ray_o[i]) / ray_d[i]
            t_near = max(t_near, min(t1, t2))
            t_far = min(t_far, max(t1, t2))
    if t_near > t_far or t_far < 0:
        return None
    return t_near

def intersect_plane(ray_o, ray_d, p_o, p_n):
    denom = np.dot(ray_d, p_n)
    if abs(denom) > 1e-6:
        t = np.dot(p_o - ray_o, p_n) / denom
        if t >= 0: return t
    return None

def render_aria_tpose():
    width, height = 800, 800
    try:
        sky_img = Image.open("/home/claw/.openclaw/workspace/sky_v4.jpg").convert("RGB")
        sw, sh = sky_img.size
        sky_pixels = sky_img.load()
    except:
        sky_img = None

    try:
        skin = Image.open("/home/claw/.openclaw/workspace/aria05_skin.png").convert("RGBA")
    except:
        skin = Image.new("RGBA", (64, 64), (255, 0, 0, 255))

    def get_color(rect):
        sx, sy, sw, sh = rect
        crop = skin.crop((sx, sy, sx+sw, sy+sh))
        arr = np.array(crop)
        if arr.size == 0: return (100, 100, 100)
        avg = arr.mean(axis=(0,1))
        return tuple(map(int, avg[:3]))

    # Camera settings
    cam_pos = np.array([0.0, 4.0, 12.0])
    light_dir = normalize(np.array([0.6, 1.0, 0.4]))
    
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    # Minecraft T-Pose Geometry (AABBs)
    # Scaled to fit scene (Base torso height at ground level approx)
    parts = [
        {"name": "Torso", "min": [-0.4, 0, -0.2], "max": [0.4, 1.2, 0.2], "tex": (20,20,8,12)},
        {"name": "Head",  "min": [-0.4, 1.2, -0.4], "max": [0.4, 2.0, 0.4], "tex": (8,8,8,8)},
        {"name": "L_Arm", "min": [-1.6, 0.8, -0.2], "max": [-0.4, 1.2, 0.2], "tex": (36,52,4,12)},
        {"name": "R_Arm", "min": [0.4, 0.8, -0.2], "max": [1.6, 1.2, 0.2], "tex": (44,20,4,12)},
        {"name": "L_Leg", "min": [-0.4, -1.2, -0.2], "max": [0.0, 0.0, 0.2], "tex": (20,52,4,12)},
        {"name": "R_Leg", "min": [0.0, -1.2, -0.2], "max": [0.4, 0.0, 0.2], "tex": (4,20,4,12)},
    ]
    
    floor_n = np.array([0.0, 1.0, 0.0])
    floor_o = np.array([0.0, -1.2, 0.0])

    print("Rendering Aria T-Pose in 3D Space...")
    for py in range(height):
        for px in range(width):
            u = (px - width/2) / (width/2)
            v = (height/2 - py) / (height/2)
            ray_d = normalize(np.array([u, v, -2.0]))

            t_min = float('inf')
            hit_color = None
            hit_pos = None
            hit_n = None

            # Floor
            tp = intersect_plane(cam_pos, ray_d, floor_o, floor_n)
            if tp and tp < t_min:
                t_min = tp
                hit_pos = cam_pos + ray_d * tp
                hit_n = floor_n
                # Grass Texture
                noise = (math.sin(hit_pos[0] * 5) * math.cos(hit_pos[2] * 5))
                hit_color = np.array([34, 139, 34]) if noise > 0.2 else np.array([50, 205, 50])

            # Character Parts
            for p in parts:
                tb = intersect_aabb(cam_pos, ray_d, np.array(p["min"]), np.array(p["max"]))
                if tb and tb < t_min:
                    t_min = tb
                    hit_pos = cam_pos + ray_d * tb
                    # Normal
                    p_min, p_max = np.array(p["min"]), np.array(p["max"])
                    hit_n = np.zeros(3)
                    for i in range(3):
                        if abs(hit_pos[i] - p_max[i]) < 0.001: hit_n[i] = 1
                        elif abs(hit_pos[i] - p_min[i]) < 0.001: hit_n[i] = -1
                    hit_n = normalize(hit_n)
                    hit_color = np.array(get_color(p["tex"]))

            if hit_color is not None:
                # Simple Shadows
                shadow_o = hit_pos + hit_n * 0.001
                in_shadow = False
                for p in parts:
                    if intersect_aabb(shadow_o, light_dir, np.array(p["min"]), np.array(p["max"])):
                        in_shadow = True
                        break
                
                shadow_factor = 0.5 if in_shadow else 1.0
                dot = max(0.2, np.dot(hit_n, light_dir))
                
                final_c = hit_color * (dot + 0.1) * shadow_factor
                pixels[px, py] = tuple(np.clip(final_c, 0, 255).astype(int))
            else:
                # Sky Mapping
                if sky_img:
                    phi = math.atan2(ray_d[0], ray_d[2])
                    theta = math.acos(ray_d[1])
                    sx = int((phi + math.pi) / (2 * math.pi) * (sw - 1))
                    sy = int(theta / math.pi * (sh - 1))
                    pixels[px, py] = sky_pixels[sx % sw, sy % sh]
                else:
                    pixels[px, py] = (135, 206, 235)

    # Polish
    img = ImageEnhance.Color(img).enhance(1.4)
    img = ImageEnhance.Contrast(img).enhance(1.2)
    img = ImageEnhance.Sharpness(img).enhance(1.3)

    timestamp = int(time.time())
    path = f"/home/claw/.openclaw/workspace/aria05_tpose_render_{timestamp}.png"
    img.save(path)
    print(f"MEDIA:{path}")

if __name__ == "__main__":
    render_aria_tpose()
