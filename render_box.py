import math
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import time

def get_rotation_matrix(rx, ry):
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    return Ry @ Rx

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

def render_box_scene():
    width, height = 800, 800
    try:
        sky_img = Image.open("/home/claw/.openclaw/workspace/sky_texture.jpg").convert("RGB")
        sky_pixels = sky_img.load()
        sw, sh = sky_img.size
    except:
        sky_img = None

    # Camera / Lighting
    cam_pos = np.array([3.0, 3.0, 8.0])
    light_dir = np.array([0.5, 1.0, 0.5])
    light_dir = light_dir / np.linalg.norm(light_dir)
    
    # Target image
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    # Geometry
    box_min = np.array([-1.0, 0.0, -1.0])
    box_max = np.array([1.0, 2.0, 1.0])
    floor_n = np.array([0.0, 1.0, 0.0])
    floor_o = np.array([0.0, 0.0, 0.0])

    print("Rendering 3D scene...")
    for py in range(height):
        for px in range(width):
            # Ray direction (simple perspective)
            u = (px - width/2) / (width/2)
            v = (height/2 - py) / (height/2)
            ray_d = np.array([u, v, -1.5])
            ray_d = ray_d / np.linalg.norm(ray_d)

            t_min = float('inf')
            hit_color = None
            hit_pos = None
            hit_normal = None

            # 1. Plane
            tp = intersect_plane(cam_pos, ray_d, floor_o, floor_n)
            if tp and tp < t_min:
                t_min = tp
                hit_pos = cam_pos + ray_d * tp
                hit_normal = floor_n
                hit_color = np.array([255, 255, 255]) # White floor

            # 2. Box
            tb = intersect_aabb(cam_pos, ray_d, box_min, box_max)
            if tb and tb < t_min:
                t_min = tb
                hit_pos = cam_pos + ray_d * tb
                # Normal for AABB
                hit_normal = np.zeros(3)
                for i in range(3):
                    if abs(hit_pos[i] - box_max[i]) < 0.001: hit_normal[i] = 1
                    elif abs(hit_pos[i] - box_min[i]) < 0.001: hit_normal[i] = -1
                hit_color = np.array([250, 250, 250]) # White box

            if hit_color is not None:
                # Shadows
                shadow_ray_o = hit_pos + hit_normal * 0.001
                ts = intersect_aabb(shadow_ray_o, light_dir, box_min, box_max)
                in_shadow = ts is not None
                
                # Shading
                dot = max(0.2, np.dot(hit_normal, light_dir))
                if in_shadow: dot *= 0.5
                
                final_c = tuple((hit_color * dot).astype(int))
                pixels[px, py] = final_c
            else:
                # Background Sky
                if sky_img:
                    # Simple equirectangular mapping for background
                    phi = math.atan2(ray_d[0], ray_d[2])
                    theta = math.acos(ray_d[1])
                    sx_coord = int((phi + math.pi) / (2 * math.pi) * (sw - 1))
                    sy_coord = int(theta / math.pi * (sh - 1))
                    pixels[px, py] = sky_pixels[sx_coord % sw, sy_coord % sh]
                else:
                    pixels[px, py] = (100, 150, 255)

    # Post processing
    print("Applying post-processing...")
    # Brightness
    img = ImageEnhance.Brightness(img).enhance(1.15)
    # Saturation
    img = ImageEnhance.Color(img).enhance(1.3)
    # Sharpness
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    # Contrast
    img = ImageEnhance.Contrast(img).enhance(1.1)

    timestamp = int(time.time())
    path = f"/home/claw/.openclaw/workspace/procedural_box_{timestamp}.png"
    img.save(path)
    print(f"MEDIA:{path}")

if __name__ == "__main__":
    render_box_scene()
