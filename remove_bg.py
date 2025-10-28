import os
import cv2
import numpy as np
from PIL import Image

def remove_background(image_path, output_path=None):
    # Read the image with alpha channel
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    # If image has no alpha channel, add one
    if img.shape[2] == 3:
        b, g, r = cv2.split(img)
        alpha = np.ones(b.shape, dtype=b.dtype) * 255
        img = cv2.merge((b, g, r, alpha))
    
    # Convert to RGBA for easier manipulation
    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    
    # Create a mask where background is white or very light
    lower_white = np.array([200, 200, 200, 0])
    upper_white = np.array([255, 255, 255, 255])
    mask = cv2.inRange(img_rgba, lower_white, upper_white)
    
    # Also check for light gray backgrounds
    lower_gray = np.array([220, 220, 220, 0])
    upper_gray = np.array([255, 255, 255, 255])
    mask_gray = cv2.inRange(img_rgba, lower_gray, upper_gray)
    
    # Combine masks
    mask = cv2.bitwise_or(mask, mask_gray)
    
    # Invert the mask to get the foreground
    mask_inv = cv2.bitwise_not(mask)
    
    # Apply the mask to the image
    img_rgba[:, :, 3] = mask_inv
    
    # Save the result
    if output_path:
        # Convert back to BGRA for saving with OpenCV
        result = cv2.cvtColor(img_rgba, cv2.COLOR_RGBA2BGRA)
        cv2.imwrite(output_path, result)
    
    return img_rgba

def process_npc_folders(base_path):
    # Get all NPC folders
    npc_folders = [f for f in os.listdir(base_path) 
                  if os.path.isdir(os.path.join(base_path, f))]
    
    for folder in npc_folders:
        folder_path = os.path.join(base_path, folder)
        print(f"Processing folder: {folder_path}")
        
        # Process all images in the folder
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    try:
                        input_path = os.path.join(root, file)
                        output_path = input_path  # Overwrite the original file
                        
                        print(f"  Processing: {file}")
                        remove_background(input_path, output_path)
                        
                    except Exception as e:
                        print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    npc_base_path = 'assets/sprites/characters/npcs/'
    process_npc_folders(npc_base_path)
    print("Background removal complete!")
