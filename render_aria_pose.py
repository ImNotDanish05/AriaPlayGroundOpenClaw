import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

def get_rotation_matrix(rx, ry, rz):
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

def project(points, w, h, scale=40, dist=25):
    # points: (N, 3)
    z = points[:, 2] + dist
    x = points[:, 0] * (w / z) * scale + w/2
    y = -points[:, 1] * (h / z) * scale + h/2 + 100
    return np.stack([x, y], axis=1)

def draw_face(canvas, skin, v2d, tex_rect):
    # tex_rect: (x, y, w, h)
    sx, sy, sw, sh = tex_rect
    face_tex = skin.crop((sx, sy, sx+sw, sy+sh)).convert("RGBA")
    
    # Target quad: TL, BL, BR, TR
    # Our v2d order for face [0,1,2,3] is TL, TR, BR, BL
    # transform(size, QUAD, data)
    # data is (TL_x, TL_y, BL_x, BL_y, BR_x, BR_y, TR_x, TR_y)
    data = (v2d[0][0], v2d[0][1], v2d[3][0], v2d[3][1], v2d[2][0], v2d[2][1], v2d[1][0], v2d[1][1])
    
    # We create a temporary high-res mask for the polygon to avoid aliasing
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).polygon([tuple(p) for p in v2d], fill=255)
    
    # Warp the texture to the canvas size
    # Note: this is expensive on large canvas. We crop to bounding box.
    bbox = [int(v2d[:,0].min()), int(v2d[:,1].min()), int(v2d[:,0].max()), int(v2d[:,1].max())]
    if bbox[0] >= canvas.width or bbox[1] >= canvas.height or bbox[2] < 0 or bbox[3] < 0: return
    
    warped = face_tex.transform(canvas.size, Image.QUAD, data, resample=Image.BILINEAR)
    canvas.paste(warped, (0,0), mask)

def render_minecraft_aria():
    width, height = 1000, 1000
    canvas = Image.new("RGBA", (width, height), (135, 206, 235, 255))
    
    # Grass ground
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 750, width, height], fill=(124, 181, 24, 255))
    
    skin = Image.open("/home/claw/.openclaw/workspace/aria05_skin.png")
    
    # Define parts with Poses
    # Name, Size(w,h,d), Offset(x,y,z), Rotation(rx,ry,rz)
    # Feminine pose: Tilted head, one arm on hip, legs slightly crossed.
    parts = [
        {"name": "Head",   "size": [8,8,8],   "pos": [0, 10, 0],   "rot": [0.1, 0.4, 0.2],   "tex": {"front": (8,8,8,8), "right": (0,8,8,8), "top": (8,0,8,8)}},
        {"name": "Torso",  "size": [8,12,4],  "pos": [0, 0, 0],    "rot": [0, 0.3, 0],       "tex": {"front": (20,20,8,12), "right": (16,20,4,12)}},
        {"name": "R_Arm",  "size": [4,12,4],  "pos": [6, 0, 0],    "rot": [0.4, 0.2, 0.3],   "tex": {"front": (44,20,4,12), "right": (40,20,4,12)}},
        {"name": "L_Arm",  "size": [4,12,4],  "pos": [-6, 1, 1],   "rot": [-0.3, 0.4, -0.2], "tex": {"front": (36,52,4,12), "right": (32,52,4,12)}},
        {"name": "R_Leg",  "size": [4,12,4],  "pos": [2, -12, 0],  "rot": [-0.1, 0.4, 0.1],  "tex": {"front": (4,20,4,12), "right": (0,20,4,12)}},
        {"name": "L_Leg",  "size": [4,12,4],  "pos": [-2, -12, 0.5],"rot": [0.2, 0.2, -0.1],  "tex": {"front": (20,52,4,12), "right": (16,52,4,12)}},
    ]

    # Rendering order: Back to front (painter's algorithm)
    # Collect all faces from all parts
    all_faces = []
    for p in parts:
        hw, hh, hd = [s/2 for s in p["size"]]
        # 8 vertices
        local_v = np.array([
            [-hw, hh, hd], [hw, hh, hd], [hw, -hh, hd], [-hw, -hh, hd], # Front
            [-hw, hh, -hd], [hw, hh, -hd], [hw, -hh, -hd], [-hw, -hh, -hd] # Back
        ])
        
        R = get_rotation_matrix(*p["rot"])
        world_v = (local_v @ R.T) + np.array(p["pos"])
        
        # Face definitions
        faces_def = [
            {"idx": [0, 1, 2, 3], "type": "front"},
            {"idx": [1, 5, 6, 2], "type": "right"},
            {"idx": [4, 0, 3, 7], "type": "left"},
            {"idx": [4, 5, 1, 0], "type": "top"},
            {"idx": [5, 4, 7, 6], "type": "back"},
            {"idx": [3, 2, 6, 7], "type": "bottom"}
        ]
        
        for f in faces_def:
            pts = world_v[f["idx"]]
            z_depth = pts[:, 2].mean()
            # Only add if we have texture for it (simplified)
            tex = p["tex"].get(f["type"], p["tex"]["front"])
            all_faces.append({"z": z_depth, "v3d": pts, "tex": tex})

    # Sort by depth
    all_faces.sort(key=lambda x: x["z"])

    for f in all_faces:
        v2d = project(f["v3d"], width, height)
        draw_face(canvas, skin, v2d, f["tex"])

    # Post Process
    canvas = canvas.convert("RGB")
    enhancer = ImageEnhance.Color(canvas)
    canvas = enhancer.enhance(1.2)
    
    path = "/home/claw/.openclaw/workspace/aria05_3d_feminine.png"
    canvas.save(path)
    print(f"MEDIA:{path}")

if __name__ == "__main__":
    render_minecraft_aria()
