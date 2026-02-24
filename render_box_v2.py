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

def render_box_scene_v2():
    width, height = 800, 800
    try:
        sky_img = Image.open("/home/claw/.openclaw/workspace/sky_v4.jpg").convert("RGB")
        sw, sh = sky_img.size
        sky_pixels = sky_img.load()
    except:
        sky_img = None

    # Camera settings
    cam_pos = np.array([0.0, 3.5, 9.0])
    light_dir = normalize(np.array([0.6, 1.0, 0.4]))
    
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    # Geometry
    box_min = np.array([-1.0, 0.0, -1.0])
    box_max = np.array([1.0, 2.0, 1.0])
    floor_n = np.array([0.0, 1.0, 0.0])
    floor_o = np.array([0.0, 0.0, 0.0])

    print("Rendering high quality 3D scene...")
    for py in range(height):
        for px in range(width):
            # Ray direction
            u = (px - width/2) / (width/2)
            v = (height/2 - py) / (height/2)
            ray_d = normalize(np.array([u, v, -1.8]))

            t_min = float('inf')
            hit_color = None
            hit_pos = None
            hit_n = None
            hit_mat = "diffuse"

            # Plane
            tp = intersect_plane(cam_pos, ray_d, floor_o, floor_n)
            if tp and tp < t_min:
                t_min = tp
                hit_pos = cam_pos + ray_d * tp
                hit_n = floor_n
                # Grass Texture (Procedural Green)
                noise = (math.sin(hit_pos[0] * 5) * math.cos(hit_pos[2] * 5))
                if noise > 0.2:
                    hit_color = np.array([34, 139, 34]) # Deep Green
                else:
                    hit_color = np.array([50, 205, 50]) # Lime Green
                hit_mat = "diffuse"

            # Box
            tb = intersect_aabb(cam_pos, ray_d, box_min, box_max)
            if tb and tb < t_min:
                t_min = tb
                hit_pos = cam_pos + ray_d * tb
                # Compute normal
                hit_n = np.zeros(3)
                for i in range(3):
                    if abs(hit_pos[i] - box_max[i]) < 0.005: hit_n[i] = 1
                    elif abs(hit_pos[i] - box_min[i]) < 0.005: hit_n[i] = -1
                hit_n = normalize(hit_n)
                hit_color = np.array([245, 245, 245])
                hit_mat = "plastic"

            if hit_color is not None:
                # Shadows (Single ray for speed, but jittered offset)
                shadow_o = hit_pos + hit_n * 0.001
                ts = intersect_aabb(shadow_o, light_dir, box_min, box_max)
                shadow_factor = 0.4 if ts else 1.0
                
                # Shading (Lambertian + Specular)
                dot = max(0.0, np.dot(hit_n, light_dir))
                
                # Ambient
                ambient = 0.2
                
                # Specular (Blinn-Phong)
                view_dir = normalize(cam_pos - hit_pos)
                half_v = normalize(light_dir + view_dir)
                spec = 0.0
                if hit_mat == "plastic":
                    spec = pow(max(0.0, np.dot(hit_n, half_v)), 32) * 0.4

                final_c = (hit_color * (dot + ambient) * shadow_factor) + (255 * spec * shadow_factor)
                pixels[px, py] = tuple(np.clip(final_c, 0, 255).astype(int))
            else:
                # Sky Mapping (Spherical)
                if sky_img:
                    phi = math.atan2(ray_d[0], ray_d[2])
                    theta = math.acos(ray_d[1])
                    sx = int((phi + math.pi) / (2 * math.pi) * (sw - 1))
                    sy = int(theta / math.pi * (sh - 1))
                    pixels[px, py] = sky_pixels[sx % sw, sy % sh]
                else:
                    pixels[px, py] = (135, 206, 235)

    # Post processing
    print("Polishing...")
    # Increase saturation and contrast
    img = ImageEnhance.Color(img).enhance(1.4)
    img = ImageEnhance.Contrast(img).enhance(1.2)
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Sharpness(img).enhance(1.3)

    timestamp = int(time.time())
    path = f"/home/claw/.openclaw/workspace/procedural_box_pro_{timestamp}.png"
    img.save(path)
    print(f"MEDIA:{path}")

if __name__ == "__main__":
    render_box_scene_v2()
