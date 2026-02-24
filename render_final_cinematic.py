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

def render_cinematic_final():
    width, height = 1260, 540
    try:
        sky_img = Image.open("/home/claw/.openclaw/workspace/sky_v4.jpg").convert("RGB")
        sw, sh = sky_img.size
        sky_pixels = sky_img.load()
    except:
        sky_img = None

    try:
        skin = Image.open("/home/claw/.openclaw/workspace/imnotdanish05_skin.png").convert("RGBA")
        skin_pixels = skin.load()
    except:
        skin = Image.new("RGBA", (64, 64), (255, 0, 0, 255))
        skin_pixels = skin.load()

    # Camera: Esthetic tilted view, FOV 20
    cam_pos = np.array([-4.0, 5.0, 28.0])
    look_at = np.array([0.0, 0.5, 0.0])
    cam_forward = normalize(look_at - cam_pos)
    
    tilt_angle = math.radians(10)
    world_up = np.array([math.sin(tilt_angle), math.cos(tilt_angle), 0.0])
    cam_right = normalize(np.cross(cam_forward, world_up))
    cam_up = np.cross(cam_right, cam_forward)
    
    fov = 20
    zoom = 1.0 / math.tan(math.radians(fov / 2))
    light_dir = normalize(np.array([0.7, 1.0, 0.5]))
    
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    # Minecraft Posed Geometry (Feminine / Natural)
    parts = [
        {"name": "Torso", "size": [0.8, 1.2, 0.4], "pos": [0, 0, 0],    "uv": (20,20,8,12)},
        {"name": "Head",  "size": [0.8, 0.8, 0.8], "pos": [0, 1.0, 0],  "uv": (8,8,8,8)},
        {"name": "L_Arm", "size": [0.4, 1.2, 0.4], "pos": [-0.6, 0, 0.2], "uv": (36,52,4,12)}, # Pose adjusted
        {"name": "R_Arm", "size": [0.4, 1.2, 0.4], "pos": [0.6, 0, 0],    "uv": (44,20,4,12)},
        {"name": "L_Leg", "size": [0.4, 1.2, 0.4], "pos": [-0.2, -1.2, 0.1], "uv": (20,52,4,12)},
        {"name": "R_Leg", "size": [0.4, 1.2, 0.4], "pos": [0.2, -1.2, 0],  "uv": (4,20,4,12)},
    ]
    
    trees = []
    random.seed(42)
    for _ in range(15):
        while True:
            tx, tz = random.uniform(-18, 18), random.uniform(-18, 12)
            if abs(tx) > 3.0 or abs(tz) > 3.0: break
        trees.append({"min": [tx-0.2, -1.2, tz-0.2], "max": [tx+0.2, 1.2, tz+0.2], "color": [101, 67, 33], "type": "tree"})
        trees.append({"min": [tx-1.2, 1.2, tz-1.2], "max": [tx+1.2, 3.8, tz+1.2], "color": [34, 139, 34], "type": "tree"})

    floor_n = np.array([0.0, 1.0, 0.0])
    floor_o = np.array([0.0, -1.2, 0.0])

    print("Rendering Cinematic Final Scene...")
    for py in range(height):
        for px in range(width):
            u = (2.0 * px / width - 1.0) * (width/height) / zoom
            v = (1.0 - 2.0 * py / height) / zoom
            ray_d = normalize(u * cam_right + v * cam_up + cam_forward)

            t_min = float('inf')
            hit_color = None
            hit_pos, hit_n = None, None

            # 1. Plane (Grass)
            tp = intersect_plane(cam_pos, ray_d, floor_o, floor_n)
            if tp and tp < t_min:
                t_min = tp
                hit_pos = cam_pos + ray_d * tp
                hit_n = floor_n
                # Procedural Grass
                noise = (math.sin(hit_pos[0] * 6) * math.cos(hit_pos[2] * 6))
                hit_color = np.array([34, 139, 34]) if noise > 0.2 else np.array([50, 205, 50])

            # 2. Geometry loop
            for p in (parts + trees):
                if "min" in p: p_min, p_max = np.array(p["min"]), np.array(p["max"])
                else: 
                    hw, hh, hd = [s/2 for s in p["size"]]
                    p_min, p_max = np.array(p["pos"]) - [hw, hh, hd], np.array(p["pos"]) + [hw, hh, hd]
                
                tb = intersect_aabb(cam_pos, ray_d, p_min, p_max)
                if tb and tb < t_min:
                    t_min = tb
                    hit_pos = cam_pos + ray_d * tb
                    hit_n = np.zeros(3)
                    for i in range(3):
                        if abs(hit_pos[i] - p_max[i]) < 0.005: hit_n[i] = 1
                        elif abs(hit_pos[i] - p_min[i]) < 0.005: hit_n[i] = -1
                    hit_n = normalize(hit_n)
                    
                    if "uv" in p:
                        u_start, v_start, u_w, v_h = p["uv"]
                        uv_x = (hit_pos[0] - p_min[0]) / (p_max[0] - p_min[0]) if abs(hit_n[2]) > 0.5 else (hit_pos[2] - p_min[2]) / (p_max[2] - p_min[2])
                        uv_y = (p_max[1] - hit_pos[1]) / (p_max[1] - p_min[1])
                        hit_color = np.array(skin_pixels[int(u_start + uv_x * u_w) % 64, int(v_start + uv_y * v_h) % 64][:3])
                    else: hit_color = np.array(p["color"])

            if hit_color is not None:
                # Basic Shading
                dot = max(0.2, np.dot(hit_n, light_dir))
                pixels[px, py] = tuple((hit_color * (dot + 0.15)).astype(int))
            else:
                # Sky
                if sky_img:
                    phi = math.atan2(ray_d[0], ray_d[2])
                    theta = math.acos(ray_d[1])
                    pixels[px, py] = sky_pixels[int((phi + math.pi) / (2 * math.pi) * (sw-1)) % sw, int(theta / math.pi * (sh-1)) % sh]
                else: pixels[px, py] = (135, 206, 235)

    # Post processing
    img = ImageEnhance.Color(img).enhance(1.4)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = img.filter(ImageFilter.SHARPEN)
    
    timestamp = int(time.time())
    path = f"/home/claw/.openclaw/workspace/imnotdanish05_final_{timestamp}.png"
    img.save(path)
    print(f"MEDIA:{path}")

if __name__ == "__main__":
    render_cinematic_final()
