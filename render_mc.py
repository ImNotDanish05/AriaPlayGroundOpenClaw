import time
import random
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

def create_minecraft_scene():
    width, height = 1200, 800
    # Background Sky (Sky blue)
    img = Image.new("RGBA", (width, height), (135, 206, 235, 255))
    draw = ImageDraw.Draw(img)

    # 1. Procedural Grass Ground
    grass_color = (124, 181, 24)
    dirt_color = (139, 69, 19)
    ground_y = 600
    
    # Draw dirt layers
    draw.rectangle([0, ground_y, width, height], fill=dirt_color)
    # Draw grass top
    draw.rectangle([0, ground_y, width, ground_y + 20], fill=grass_color)
    
    # Add blocky details to ground
    for i in range(100):
        bx = random.randint(0, width)
        by = random.randint(ground_y, height)
        bw, bh = random.randint(10, 40), random.randint(10, 40)
        draw.rectangle([bx, by, bx+bw, by+bh], fill=(120, 60, 10, 255))

    # 2. Draw blocky clouds
    for _ in range(5):
        cx = random.randint(0, width)
        cy = random.randint(50, 200)
        cw = random.randint(100, 300)
        draw.rectangle([cx, cy, cx+cw, cy+40], fill=(255, 255, 255, 200))

    # 3. Draw blocky Sun
    draw.rectangle([1000, 80, 1120, 200], fill=(255, 255, 0, 255))

    # 4. Load and paste Aria05 Character
    try:
        char_img = Image.open("/home/claw/.openclaw/workspace/aria05_alex.png").convert("RGBA")
        # Position character on ground
        char_w, char_h = char_img.size
        paste_x = (width - char_w) // 2
        paste_y = ground_y - char_h + 40 # slightly overlap grass
        img.paste(char_img, (paste_x, paste_y), char_img)
    except Exception as e:
        print(f"Error pasting character: {e}")

    # 5. Post processing (Procedural Shaders)
    # Increase saturation for that "Minecraft Vibe"
    converter = ImageEnhance.Color(img)
    img = converter.enhance(1.4)
    
    # Add a soft vignette/lighting from top right (sun)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for r in range(width, 0, -50):
        alpha = int(100 * (r / width))
        ov_draw.ellipse([1100-r, 140-r, 1100+r, 140+r], outline=None, fill=(255, 255, 200, 20))
    img = Image.alpha_composite(img, overlay)

    timestamp = int(time.time())
    filename = f"/home/claw/.openclaw/workspace/mc-aria05-{timestamp}.png"
    img.save(filename)
    print(f"MEDIA:{filename}")
    return filename

if __name__ == "__main__":
    create_minecraft_scene()
