from PIL import Image, ImageDraw

# Canvas
W, H = 1024, 1024
bg = (10, 12, 20)
img = Image.new("RGB", (W, H), bg)
ctx = ImageDraw.Draw(img)

cx, cy = W // 2, H // 2 + 40

# Helper for circles
def circle(x, y, r, fill):
    ctx.ellipse((x-r, y-r, x+r, y+r), fill=fill)

# Hologram ring
ring_outer = 360
ring_inner = 300
ctx.ellipse((cx-ring_outer, cy-ring_outer, cx+ring_outer, cy+ring_outer), outline=(120, 200, 255), width=4)
ctx.ellipse((cx-ring_inner, cy-ring_inner, cx+ring_inner, cy+ring_inner), outline=(30, 60, 100), width=2)

# Head
skin = (244, 220, 210)
head_r = 180
circle(cx, cy-120, head_r, skin)

# Hair base
hair_dark = (25, 25, 40)
ctx.pieslice((cx-210, cy-340, cx+210, cy+60), start=200, end=340, fill=hair_dark)

# Hair side locks
ctx.polygon([
    (cx-210, cy-80),
    (cx-80, cy+120),
    (cx-40, cy+40)
], fill=hair_dark)
ctx.polygon([
    (cx+210, cy-80),
    (cx+80, cy+120),
    (cx+40, cy+40)
], fill=hair_dark)

# Hair highlight strip
highlight = (120, 130, 220)
ctx.rectangle((cx-210, cy-260, cx+210, cy-210), fill=highlight)

# Bangs
ctx.polygon([
    (cx-210, cy-200),
    (cx-40, cy-40),
    (cx-20, cy-200)
], fill=hair_dark)
ctx.polygon([
    (cx+210, cy-200),
    (cx+40, cy-40),
    (cx+20, cy-200)
], fill=hair_dark)

# Eyes
eye_w, eye_h = 90, 60
left_eye_box = (cx-110-eye_w//2, cy-70-eye_h//2, cx-110+eye_w//2, cy-70+eye_h//2)
right_eye_box = (cx+110-eye_w//2, cy-70-eye_h//2, cx+110+eye_w//2, cy-70+eye_h//2)

# Eye whites
ctx.rounded_rectangle(left_eye_box, radius=25, fill=(235, 245, 255))
ctx.rounded_rectangle(right_eye_box, radius=25, fill=(235, 245, 255))

# Iris gradient-ish blocks
iris_blue = (120, 200, 255)
iris_purple = (180, 150, 255)
for box in (left_eye_box, right_eye_box):
    x1, y1, x2, y2 = box
    mid = (x1 + x2)//2
    ctx.rounded_rectangle((x1+8, y1+10, mid, y2-8), radius=18, fill=iris_blue)
    ctx.rounded_rectangle((mid, y1+10, x2-8, y2-8), radius=18, fill=iris_purple)

# Pupils
circle(cx-110, cy-70, 10, (20, 30, 50))
circle(cx+110, cy-70, 10, (20, 30, 50))

# Eye shine
circle(cx-125, cy-80, 6, (255, 255, 255))
circle(cx+95, cy-80, 6, (255, 255, 255))

# Mouth (small smirk)
smile_y = cy+10
ctx.arc((cx-40, smile_y-10, cx+40, smile_y+30), start=200, end=340, fill=(80, 40, 60), width=4)

# Body hoodie
body_top = cy+60
body_bottom = cy+360
hoodie = (235, 240, 250)
ctx.rounded_rectangle((cx-260, body_top, cx+260, body_bottom), radius=60, fill=hoodie)

# Hoodie stripes
ctx.rectangle((cx-260, body_top+40, cx-230, body_bottom-40), fill=(120, 200, 255))
ctx.rectangle((cx+230, body_top+40, cx+260, body_bottom-40), fill=(180, 150, 255))

# Inner shirt text area
inner = (30, 34, 60)
ctx.rounded_rectangle((cx-160, body_top+40, cx+160, body_top+150), radius=30, fill=inner)

# Simple text substitute (blocks) for "WE WIN THESE"
ctx.rectangle((cx-130, body_top+75, cx-60, body_top+90), fill=(240, 240, 240))
ctx.rectangle((cx-40, body_top+75, cx+40, body_top+90), fill=(200, 240, 240))
ctx.rectangle((cx+60, body_top+75, cx+130, body_top+90), fill=(240, 220, 240))

# Mug
mug_x, mug_y = cx+170, body_top+200
ctx.rounded_rectangle((mug_x-60, mug_y-60, mug_x+40, mug_y+40), radius=20, fill=(230, 220, 255))
ctx.ellipse((mug_x+30, mug_y-15, mug_x+70, mug_y+15), outline=(210, 200, 240), width=6)

# Steam lines
ctx.line((mug_x-15, mug_y-80, mug_x-5, mug_y-60), fill=(230, 230, 255), width=3)
ctx.line((mug_x+5, mug_y-85, mug_x+15, mug_y-65), fill=(230, 230, 255), width=3)

# Fox emblem on hoodie
fox_cx, fox_cy = cx-200, body_top+80
ctx.polygon([
    (fox_cx, fox_cy-20),
    (fox_cx-25, fox_cy+10),
    (fox_cx+25, fox_cy+10)
], fill=(255, 160, 120))
ctx.rectangle((fox_cx-12, fox_cy+10, fox_cx+12, fox_cy+28), fill=(255, 200, 150))

# Background floating panels
panel_color = (30, 50, 90)
ctx.rounded_rectangle((cx-420, cy-260, cx-260, cy-140), radius=20, fill=panel_color)
ctx.rounded_rectangle((cx+260, cy-260, cx+420, cy-140), radius=20, fill=panel_color)
ctx.rounded_rectangle((cx-420, cy+40, cx-260, cy+160), radius=20, fill=panel_color)

img.save("/home/claw/.openclaw/workspace/aria_art/aria_icon.png")
print("Saved to aria_art/aria_icon.png")
