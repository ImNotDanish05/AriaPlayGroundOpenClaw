import math
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

def get_rotation_matrix(rx, ry, rz):
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

def project(points, w, h, scale=25, dist=40):
    # scale down to fit 1000px canvas
    z = points[:, 2] + dist
    x = points[:, 0] * (w / dist) * scale + w/2
    y = -points[:, 1] * (h / dist) * scale + h/2 + 50
    return np.stack([x, y], axis=1)

def render_minecraft_aria_v2():
    width, height = 1000, 1000
    # Background
    canvas = Image.new("RGB", (width, height), (135, 206, 235))
    draw = ImageDraw.Draw(canvas)
    
    # Grass ground
    draw.rectangle([0, 700, width, height], fill=(124, 181, 24))
    
    # Load skin for colors
    try:
        skin = Image.open("/home/claw/.openclaw/workspace/aria05_skin.png").convert("RGBA")
    except:
        # Fallback if skin not found
        skin = Image.new("RGBA", (64, 64), (255, 0, 0, 255))

    def get_avg_color(rect):
        sx, sy, sw, sh = rect
        crop = skin.crop((sx, sy, sx+sw, sy+sh))
        # Filter out transparency if possible, or just average
        arr = np.array(crop)
        if arr.size == 0: return (100, 100, 100)
        avg = arr.mean(axis=(0,1))
        return tuple(map(int, avg[:3]))

    # Define parts with Poses (More natural, less "crampy")
    # Tilted head, one arm slightly out, legs neutral
    parts = [
        {"name": "Head",   "size": [8,8,8],   "pos": [0, 11, 0],    "rot": [0.05, 0.3, 0.1],  "tex": (8,8,8,8)},
        {"name": "Torso",  "size": [8,12,4],  "pos": [0, 0, 0],     "rot": [0, 0.2, 0],       "tex": (20,20,8,12)},
        {"name": "R_Arm",  "size": [4,12,4],  "pos": [6, 0, 1],     "rot": [-0.2, 0, 0.2],    "tex": (44,20,4,12)},
        {"name": "L_Arm",  "size": [4,12,4],  "pos": [-6, 0, 0],    "rot": [0.1, 0.2, -0.15], "tex": (36,52,4,12)},
        {"name": "R_Leg",  "size": [4,12,4],  "pos": [2, -12, 0],   "rot": [0, 0.1, 0],       "tex": (4,20,4,12)},
        {"name": "L_Leg",  "size": [4,12,4],  "pos": [-2, -12, 0.2],"rot": [0, -0.1, 0],      "tex": (20,52,4,12)},
    ]

    all_faces = []
    light_dir = np.array([0.5, 1, 0.5])
    light_dir = light_dir / np.linalg.norm(light_dir)

    for p in parts:
        hw, hh, hd = [s/2 for s in p["size"]]
        # 8 vertices of a box
        local_v = np.array([
            [-hw, hh, hd], [hw, hh, hd], [hw, -hh, hd], [-hw, -hh, hd], # Front 0,1,2,3
            [-hw, hh, -hd], [hw, hh, -hd], [hw, -hh, -hd], [-hw, -hh, -hd] # Back 4,5,6,7
        ])
        
        R = get_rotation_matrix(*p["rot"])
        world_v = (local_v @ R.T) + np.array(p["pos"])
        
        # Face definitions with normals for shading
        faces_def = [
            {"idx": [0, 1, 2, 3], "n": [0, 0, 1]},   # Front
            {"idx": [1, 5, 6, 2], "n": [1, 0, 0]},   # Right
            {"idx": [4, 0, 3, 7], "n": [-1, 0, 0]},  # Left
            {"idx": [4, 5, 1, 0], "n": [0, 1, 0]},   # Top
            {"idx": [5, 4, 7, 6], "n": [0, 0, -1]},  # Back
            {"idx": [3, 2, 6, 7], "n": [0, -1, 0]}   # Bottom
        ]
        
        base_color = get_avg_color(p["tex"])
        
        for f in faces_def:
            pts = world_v[f["idx"]]
            z_depth = pts[:, 2].mean()
            
            # Shading
            rotated_n = R @ np.array(f["n"])
            dot = np.dot(rotated_n, light_dir)
            brightness = max(0.4, dot)
            face_color = tuple(int(c * brightness) for c in base_color)
            
            all_faces.append({"z": z_depth, "pts": pts, "color": face_color})

    # Sort by depth (Back to Front)
    all_faces.sort(key=lambda x: x["z"], reverse=True)

    for f in all_faces:
        v2d = project(f["pts"], width, height)
        draw.polygon([tuple(p) for p in v2d], fill=f["color"], outline=f["color"])

    # Polish
    enhancer = ImageEnhance.Color(canvas)
    canvas = enhancer.enhance(1.3)
    
    path = "/home/claw/.openclaw/workspace/aria05_3d_feminine_v3.png"
    canvas.save(path)
    print(f"MEDIA:{path}")

if __name__ == "__main__":
    render_minecraft_aria_v2()
