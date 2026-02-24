import math
import time
from PIL import Image, ImageDraw, ImageEnhance

def intersect_aabb(ray_o, ray_d, box_min, box_max):
    t_near = -float('inf')
    t_far = float('inf')
    for i in range(3):
        if abs(ray_d[i]) < 1e-6:
            if ray_o[i] < box_min[i] or ray_o[i] > box_max[i]:
                return None, None
        else:
            t1 = (box_min[i] - ray_o[i]) / ray_d[i]
            t2 = (box_max[i] - ray_o[i]) / ray_d[i]
            t_near = max(t_near, min(t1, t2))
            t_far = min(t_far, max(t1, t2))
    
    if t_near > t_far or t_far < 0:
        return None, None
    return t_near, t_far

def intersect_plane(ray_o, ray_d, p_o, p_n):
    denom = sum(ray_d[i] * p_n[i] for i in range(3))
    if abs(denom) > 1e-6:
        t = sum((p_o[i] - ray_o[i]) * p_n[i] for i in range(3)) / denom
        if t >= 0: return t
    return None

def render_3d_house():
    width, height = 800, 800
    img = Image.new("RGB", (width, height), (135, 206, 235)) # Sky
    pixels = img.load()

    # Camera / Ray setup
    # Look from top-front-right
    cam_pos = [4, 4, 10]
    light_dir = [0.5, 1, 0.2]
    l_len = math.sqrt(sum(x**2 for x in light_dir))
    light_dir = [x/l_len for x in light_dir]

    print("Rendering 3D Minimalist House...")

    for py in range(height):
        for px in range(width):
            # Simple perspective-ish ray
            u = (px - width/2) / (width/2)
            v = (height/2 - py) / (height/2)
            ray_d = [u, v, -1] # Direction
            # Rotate ray slightly for better view
            d_len = math.sqrt(sum(x**2 for x in ray_d))
            ray_d = [x/d_len for x in ray_d]
            
            # Intersection tests
            t_min_hit = float('inf')
            hit_color = None

            # 1. Ground Plane (y = 0)
            tp = intersect_plane(cam_pos, ray_d, [0, 0, 0], [0, 1, 0])
            if tp and tp < t_min_hit:
                t_min_hit = tp
                # Checkered grass/dirt pattern
                hit_pos = [cam_pos[i] + ray_d[i] * tp for i in range(3)]
                if (int(hit_pos[0]) + int(hit_pos[2])) % 2 == 0:
                    hit_color = (100, 200, 100)
                else:
                    hit_color = (80, 180, 80)

            # 2. House Base (AABB)
            # Center at 0,0,0, size 2x2x2
            tb_near, tb_far = intersect_aabb(cam_pos, ray_d, [-1, 0, -1], [1, 2, 1])
            if tb_near and tb_near < t_min_hit:
                t_min_hit = tb_near
                hit_color = (240, 240, 240) # White walls
                # Simple shadow calculation on side
                hit_pos = [cam_pos[i] + ray_d[i] * tb_near for i in range(3)]
                # Determine normal based on which face was hit
                if abs(hit_pos[0] - 1) < 0.01: n = [1,0,0]
                elif abs(hit_pos[0] + 1) < 0.01: n = [-1,0,0]
                elif abs(hit_pos[1] - 2) < 0.01: n = [0,1,0]
                elif abs(hit_pos[1] - 0) < 0.01: n = [0,-1,0]
                elif abs(hit_pos[2] - 1) < 0.01: n = [0,0,1]
                else: n = [0,0,-1]
                
                dot = sum(n[i] * light_dir[i] for i in range(3))
                hit_color = tuple(int(c * max(0.3, dot)) for c in hit_color)

            # 3. Roof (Simulated with a smaller box/slope logic for simplicity)
            # Let's just do a dark grey flat-ish roof for now to ensure reliability
            tr_near, tr_far = intersect_aabb(cam_pos, ray_d, [-1.2, 2, -1.2], [1.2, 2.3, 1.2])
            if tr_near and tr_near < t_min_hit:
                t_min_hit = tr_near
                hit_color = (60, 60, 70) # Dark roof
                dot = 0.9 # Top is usually bright
                hit_color = tuple(int(c * dot) for c in hit_color)

            if hit_color:
                pixels[px, py] = hit_color

    # Post processing
    converter = ImageEnhance.Color(img)
    img = converter.enhance(1.2)
    
    timestamp = int(time.time())
    filename = f"/home/claw/.openclaw/workspace/house-3d-{timestamp}.png"
    img.save(filename)
    print(f"MEDIA:{filename}")

if __name__ == "__main__":
    render_3d_house()
