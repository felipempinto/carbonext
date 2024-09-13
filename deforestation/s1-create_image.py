import numpy as np
import rasterio

input_image1 = "deforestation/data/sentinel2_image_2018_0.tif"
input_image2 = "deforestation/data/sentinel2_image_2021_0.tif"
label_image1 = "deforestation/data/MapBiomas_2018_0.tif"
label_image2 = "deforestation/data/MapBiomas_2021_0_Real.tif"
change_value = 255

# Function to process a single image by extracting bands and generating binary mask based on label 3
def process_image(image_path, bands=[8, 2, 3]):
    with rasterio.open(image_path) as src:
        image = np.stack([src.read(b) for b in bands], axis=0)
    return image

def get_label(image_path, label_value=3):
    with rasterio.open(image_path) as src:
        label = src.read(1)
        binary_label = np.where(label == label_value, 1, 0)
    return binary_label

def create_change_detection_label(label1, label2, change_value=255):
    change_map = np.where(label1 != label2, change_value, 0)
    return change_map

# Get the binary labels from the input label images
binary_label1 = get_label(label_image1)
binary_label2 = get_label(label_image2)

# Create the change detection label
change_label = create_change_detection_label(binary_label1, binary_label2, change_value=change_value)

# Add projection and transform from the input image
with rasterio.open(label_image1) as src:
    profile = src.profile
    transform = src.transform
    crs = src.crs

# Update the profile to match the change detection output
profile.update(driver='GTiff', height=change_label.shape[0], width=change_label.shape[1], count=1, dtype=rasterio.uint8, crs=crs, transform=transform)

# Save the change detection label with the same projection and transform as the input
output_label_path = 'change_label.tif'
with rasterio.open(output_label_path, 'w', **profile) as dst:
    dst.write(change_label.astype(np.uint8), 1)

print(f"Change detection label saved at {output_label_path} with correct projection and transform.")
