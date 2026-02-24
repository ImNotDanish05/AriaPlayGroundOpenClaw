from PIL import Image

def merge_images():
    # Paths to the images
    img_paths = [
        'maskots/ui_ux.webp',
        'maskots/ctf.webp',
        'maskots/web.webp'
    ]
    
    images = [Image.open(p) for p in img_paths]
    
    # Get dimensions
    widths, heights = zip(*(i.size for i in images))
    
    total_width = sum(widths)
    max_height = max(heights)
    
    # Create new image with a transparent background (if they are transparent)
    # or white if not. Webp usually supports alpha.
    new_img = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))
    
    x_offset = 0
    for img in images:
        # To avoid "downgrading", we don't resize. 
        # If heights differ, we align them to the center or top.
        # Let's align to the center vertically.
        y_offset = (max_height - img.height) // 2
        new_img.paste(img, (x_offset, y_offset))
        x_offset += img.width
        
    # Save the result
    # Saving as PNG to preserve absolute quality (lossless)
    # Or save as webp with lossless=True
    output_path = 'maskots/merged_maskots.png'
    new_img.save(output_path, 'PNG', optimize=True)
    print(f"Saved merged image to {output_path}")

if __name__ == "__main__":
    merge_images()
