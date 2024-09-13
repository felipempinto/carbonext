

import numpy as np
import rasterio
from rasterio.windows import Window
from PIL import Image
import os

# Paths to input images and labels
input_image1 = "deforestation/data/to_chip/image1_bands.tif"
input_image2 = "deforestation/data/to_chip/image2_bands.tif"
label_image = "deforestation/data/to_chip/change_label.tif"
output_dir = "deforestation/data/chips"
chip_size = (256, 256)  # Define the size of each chip (width, height)
overlap_fraction = 0.25  # 25% overlap

def save_chip_as_png(chip, path):
    """ Save a chip as a PNG file. """
    if chip.ndim == 3:  # Multi-band image
        # Normalize the image to 0-255
        chip = np.clip(chip, 0, 255).astype(np.uint8)
        # Convert to PIL Image and save
        img = Image.fromarray(np.moveaxis(chip, 0, -1))  # Move channels to last dimension for PIL
    else:  # Single-band image
        chip = np.clip(chip, 0, 255).astype(np.uint8)
        img = Image.fromarray(chip, mode='L')
    
    img.save(path)

def normalize(img):
    min_val = img.min()
    max_val = img.max()
    if max_val > min_val:
        return ((img - min_val) / (max_val - min_val))*255
    else:
        return img  # No normalization if max and min are the same

def create_chips(image1_path, image2_path, label_path, chip_size, overlap_fraction, output_dir_img1, output_dir_img2, output_dir_label):
    with rasterio.open(image1_path) as src_image1, \
        rasterio.open(image2_path) as src_image2, \
        rasterio.open(label_path) as src_label:
        
        image_width = src_image1.width
        image_height = src_image1.height
        overlap = int(chip_size[0] * overlap_fraction)
        step_size = chip_size[0] - overlap
        
        # Make sure the output directories exist
        os.makedirs(output_dir_img1, exist_ok=True)
        os.makedirs(output_dir_img2, exist_ok=True)
        os.makedirs(output_dir_label, exist_ok=True)

        chip_index = 0
        
        # Loop through the image with overlap
        for i in range(0, image_height - chip_size[1] + 1, step_size):
            for j in range(0, image_width - chip_size[0] + 1, step_size):
                # Define the window for the chip
                window = Window(j, i, chip_size[0], chip_size[1])
                
                # Read the chip data from image1, image2, and label
                image1_chip = src_image1.read(window=window)
                image2_chip = src_image2.read(window=window)
                label_chip = src_label.read(1, window=window)

                # Normalize each band of the image chips
                for band in range(image1_chip.shape[0]):
                    image1_chip[band] = normalize(image1_chip[band])
                for band in range(image2_chip.shape[0]):
                    image2_chip[band] = normalize(image2_chip[band])

                # Define output file paths
                image1_chip_path = os.path.join(output_dir_img1, f'chip_{chip_index}.png')
                image2_chip_path = os.path.join(output_dir_img2, f'chip_{chip_index}.png')
                label_chip_path = os.path.join(output_dir_label, f'chip_{chip_index}.png')
                
                # Save the chips to PNG files
                save_chip_as_png(image1_chip, image1_chip_path)
                save_chip_as_png(image2_chip, image2_chip_path)
                save_chip_as_png(label_chip, label_chip_path)
                
                chip_index += 1

# Create chips for the images and labels
create_chips(input_image1, input_image2, label_image, chip_size, overlap_fraction, 
            os.path.join(output_dir, 'A'), 
            os.path.join(output_dir, 'B'), 
            os.path.join(output_dir, 'label'))
