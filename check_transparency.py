import sys
from PIL import Image

def check_transparency(image_path):
    try:
        img = Image.open(image_path)
        print(f"Image: {image_path}")
        print(f"Mode: {img.mode}")
        print(f"Size: {img.size}")
        
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            print("Has alpha channel: Yes")
            
            # Check if any pixels are transparent
            if img.mode == 'RGBA':
                # For RGBA images, check the alpha channel
                alpha = img.getchannel('A')
                has_transparency = any(px < 255 for px in alpha.getdata())
            else:
                # For other modes with alpha, check if the image has a transparency mask
                has_transparency = img.info.get('transparency') is not None
                
            print(f"Has transparent pixels: {has_transparency}")
            
            # Count transparent pixels
            if has_transparency:
                if img.mode == 'RGBA':
                    transparent_pixels = sum(1 for px in alpha.getdata() if px < 255)
                    total_pixels = img.size[0] * img.size[1]
                    print(f"Transparent pixels: {transparent_pixels}/{total_pixels} ({(transparent_pixels/total_pixels)*100:.1f}%)")
        else:
            print("Has alpha channel: No")
            print("Note: Image doesn't have an alpha channel")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_transparency(sys.argv[1])
    else:
        print("Please provide an image file path as an argument")
