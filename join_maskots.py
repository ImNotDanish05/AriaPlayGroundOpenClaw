import sys
from PIL import Image

def join_images():
    try:
        # Order: UI/UX (Kiri), CTF (Tengah), WEB (Kanan)
        img1 = Image.open('maskots/ui_ux.webp')
        img2 = Image.open('maskots/ctf.webp')
        img3 = Image.open('maskots/web.webp')

        widths, heights = zip(*(i.size for i in [img1, img2, img3]))

        total_width = sum(widths)
        max_height = max(heights)

        new_im = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))

        x_offset = 0
        for im in [img1, img2, img3]:
            y_offset = (max_height - im.size[1]) // 2
            new_im.paste(im, (x_offset, y_offset))
            x_offset += im.size[0]

        output_path = 'maskot_combined.webp'
        new_im.save(output_path, 'WEBP', lossless=True)
        print(f"Success: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    join_images()
