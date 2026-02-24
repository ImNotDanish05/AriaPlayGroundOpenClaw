import math
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import time
import random

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

def render_aria_forest():
    width, height = 800, 800
    try:
        sky_img = Image.open("/home/claw/.openclaw/workspace/sky_v4.jpg").convert("RGB")
        sw, sh = sky_img.size
        sky_pixels = sky_img.load()
    except:
        sky_img = None

    try:
        skin = Image.open("/home/claw/.openclaw/workspace/aria05_skin.png").convert("RGBA")
        skin_pixels = skin.load()
    except:
        skin = Image.new("RGBA", (64, 64), (255, 0, 0, 255))
        skin_pixels = skin.load()

    # Camera settings
    cam_pos = np.array([0.0, 4.0, 15.0])
    light_dir = normalize(np.array([0.6, 1.0, 0.4]))
    
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    # Minecraft T-Pose Geometry
    parts = [
        {"name": "Torso", "min": [-0.4, 0, -0.2], "max": [0.4, 1.2, 0.2], "uv": (20,20,8,12), "type": "player"},
        {"name": "Head",  "min": [-0.4, 1.2, -0.4], "max": [0.4, 2.0, 0.4], "uv": (8,8,8,8), "type": "player"},
        {"name": "L_Arm", "min": [-1.6, 0.8, -0.2], "max": [-0.4, 1.2, 0.2], "uv": (36,52,4,12), "type": "player"},
        {"name": "R_Arm", "min": [0.4, 0.8, -0.2], "max": [1.6, 1.2, 0.2], "uv": (44,20,4,12), "type": "player"},
        {"name": "L_Leg", "min": [-0.4, -1.2, -0.2], "max": [0.0, 0.0, 0.2], "uv": (20,52,4,12), "type": "player"},
        {"name": "R_Leg", "min": [0.0, -1.2, -0.2], "max": [0.4, 0.0, 0.2], "uv": (4,20,4,12), "type": "player"},
    ]
    
    # Tree Generation
    trees = []
    random.seed(42) # Consistent forest
    for _ in range(8):
        # Position trees away from center
        while True:
            tx = random.uniform(-10, 10)
            tz = random.uniform(-10, 5)
            if abs(tx) > 2.5 or abs(tz) > 2.5: # Don't block the center
                break
        
        # Trunk
        trunk_min = [tx - 0.2, -1.2, tz - 0.2]
        trunk_max = [tx + 0.2, 0.8, tz + 0.2]
        trees.append({"min": trunk_min, "max": trunk_max, "color": [101, 67, 33], "type": "tree"})
        # Leaves
        leaf_min = [tx - 1.0, 0.8, tz - 1.0]
        leaf_max = [tx + 1.0, 2.5, tz + 1.0]
        trees.append({"min": leaf_min, "max": leaf_max, "color": [34, 139, 34], "type": "tree"})

    all_geometry = parts + trees
    
    floor_n = np.array([0.0, 1.0, 0.0])
    floor_o = np.array([0.0, -1.2, 0.0])

    print("Rendering Aria in the Forest...")
    for py in range(height):
        for px in range(width):
            u = (px - width/2) / (width/2)
            v = (height/2 - py) / (height/2)
            ray_d = normalize(np.array([u, v, -2.5]))

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
                noise = (math.sin(hit_pos[0] * 5) * math.cos(hit_pos[2] * 5))
                hit_color = np.array([34, 139, 34]) if noise > 0.2 else np.array([50, 205, 50])

            # Geometry (Player + Trees)
            for g in all_geometry:
                g_min, g_max = np.array(g["min"]), np.array(g["max"])
                tb = intersect_aabb(cam_pos, ray_d, g_min, g_max)
                if tb and tb < t_min:
                    t_min = tb
                    hit_pos = cam_pos + ray_d * tb
                    
                    # Normal calculation
                    local_n = np.zeros(3)
                    uv_x, uv_y = 0, 0
                    
                    if abs(hit_pos[2] - g_max[2]) < 0.001: # Front
                        local_n = np.array([0,0,1])
                        uv_x = (hit_pos[0] - g_min[0]) / (g_max[0] - g_min[0])
                        uv_y = (g_max[1] - hit_pos[1]) / (g_max[1] - g_min[1])
                    elif abs(hit_pos[1] - g_max[1]) < 0.001: # Top
                        local_n = np.array([0,1,0])
                        uv_x = (hit_pos[0] - g_min[0]) / (g_max[0] - g_min[0])
                        uv_y = (hit_pos[2] - g_min[2]) / (g_max[2] - g_min[2])
                    else:
                        local_n = np.array([1,0,0]) # Side
                        uv_x = (hit_pos[2] - g_min[2]) / (g_max[2] - g_min[2])
                        uv_y = (g_max[1] - hit_pos[1]) / (g_max[1] - g_min[1])

                    hit_n = normalize(local_n)
                    
                    if g["type"] == "player":
                        u_start, v_start, u_w, v_h = g["uv"]
                        px_x = int(u_start + uv_x * (u_w - 0.01))
                        px_y = int(v_start + uv_y * (v_h - 0.01))
                        hit_color = np.array(skin_pixels[px_x % 64, px_y % 64][:3])
                    else:
                        hit_color = np.array(g["color"])

            if hit_color is not None:
                # Shadows
                shadow_o = hit_pos + hit_n * 0.001
                in_shadow = False
                for g in all_geometry:
                    if intersect_aabb(shadow_o, light_dir, np.array(g["min"]), np.array(g["max"])):
                        in_shadow = True
                        break
                
                shadow_factor = 0.55 if in_shadow else 1.0
                dot = max(0.2, np.dot(hit_n, light_dir))
                
                final_c = hit_color * (dot + 0.1) * shadow_factor
                pixels[px, py] = tuple(np.clip(final_c, 0, 255).astype(int))
            else:
                if sky_img:
                    phi = math.atan2(ray_d[0], ray_d[2])
                    theta = math.acos(ray_d[1])
                    sx = int((phi + math.pi) / (2 * math.pi) * (sw - 1))
                    sy = int(theta / math.pi * (sh - 1))
                    pixels[px, py] = sky_pixels[sx % sw, sy % sh]
                else:
                    pixels[px, py] = (135, 206, 235)

    # Post processing
    img = ImageEnhance.Color(img).enhance(1.3)
    img = ImageEnhance.Contrast(img).enhance(1.1)
    img = ImageEnhance.Sharpness(img).enhance(1.5)

    timestamp = int(time.time())
    path = f"/home/claw/.openclaw/workspace/aria05_forest_{timestamp}.png"
    img.save(path)
    print(f"MEDIA:{path}")

if __name__ == "__main__":
    render_aria_forest()
