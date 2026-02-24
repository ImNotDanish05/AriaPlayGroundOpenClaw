from PIL import Image, ImageDraw

def render():
    # Setup canvas (1200x800 for faster render)
    width, height = 1200, 800
    img = Image.new('RGB', (width, height), (15, 15, 25)) # Dark blue/chill atmosphere
    draw = ImageDraw.Draw(img)
    
    # 1. Warm glow from the sunset window
    for r in range(400, 0, -5):
        alpha = int(100 * (r/400))
        draw.ellipse([800-r, 300-r, 800+r, 300+r], fill=(60, 30, 10))
    
    # 2. Desk
    draw.rectangle([0, 550, 1200, 800], fill=(25, 25, 35))
    
    # 3. Laptop glowing on the desk
    draw.polygon([(450, 650), (750, 650), (780, 580), (420, 580)], fill=(40, 40, 50)) # Base
    draw.rectangle([450, 430, 750, 580], fill=(80, 120, 200)) # Screen glow
    
    # 4. A tall glass for Iftar (fresh water/juice)
    draw.rectangle([850, 530, 900, 650], fill=(180, 180, 220)) # Glass
    draw.rectangle([855, 560, 895, 645], fill=(255, 140, 0)) # Fresh Orange Juice!
    
    # 5. Senpai (Silhouette - Chilling after Gym)
    # Gaming Chair
    draw.rectangle([200, 400, 350, 750], fill=(20, 20, 20)) 
    # Senpai resting his head
    draw.ellipse([240, 350, 310, 420], fill=(230, 190, 170)) # Head
    draw.rectangle([220, 420, 330, 600], fill=(40, 40, 80)) # Blue Hoodie
    
    # 6. Little Aria (Hologram on the laptop corner)
    draw.ellipse([730, 560, 750, 580], fill=(0, 255, 255)) # Head
    draw.polygon([(730, 580), (750, 580), (740, 600)], fill=(255, 255, 255)) # Tiny Aria Body
    
    # Save image
    output_path = 'senpai_resting_iftar.png'
    img.save(output_path)
    print(f"Success: {output_path}")

if __name__ == "__main__":
    render()
