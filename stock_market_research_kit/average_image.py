import numpy as np
import glob
import os
import skimage.filters.rank as rank
from skimage import img_as_ubyte, io
from skimage.morphology import disk


def remove_gray_background(image, background_threshold=241):
    # Create a binary mask where the image is darker than the background_threshold
    non_background_mask = image < background_threshold

    # Set the pixels where the mask is True to the original image values, and the others to white (255)
    no_background_image = np.where(non_background_mask, image, 255)

    return no_background_image


def highlight_darker_areas(image, disk_radius=5, alpha=0.05):
    # Ensure the image is in the range [0, 255] and its type is uint8
    image = img_as_ubyte(image)

    # Calculate the mean local threshold using the rank.mean function
    local_mean_threshold = rank.mean(image, disk(disk_radius))

    # Create a binary mask where the original image is darker than the local_mean_threshold
    darker_areas_mask = image < local_mean_threshold

    # Convert the mask to uint8 and scale it to the range [0, 255]
    darker_areas_mask = img_as_ubyte(darker_areas_mask)

    # Blend the original image and the darker_areas_mask to highlight the darker areas
    highlighted_image = (1 - alpha) * image + alpha * darker_areas_mask

    # Remove the gray background color
    no_background_image = remove_gray_background(highlighted_image)

    return no_background_image


def average_images(image_folder, output_path):
    # Read all image paths
    image_files = glob.glob(os.path.join(image_folder, "*.png"))

    # Load the first image to get the dimensions
    img = io.imread(image_files[0])
    height, width = img.shape

    # Initialize an empty array of the same size as the images
    avg_image = np.zeros((height, width), dtype=np.float32)

    # Loop through all images in the folder
    for image_file in image_files:
        # Read and convert the image to float32
        img = io.imread(image_file).astype(np.float32)

        # Add the image to the average
        avg_image += img / len(image_files)

    # Normalize the average image and convert it back to uint8
    avg_image = np.clip(avg_image, 0, 255).astype(np.uint8)

    # Highlight darker areas in the grayscale image
    highlighted_image = highlight_darker_areas(avg_image)

    # Save the image to the output path
    io.imsave(output_path, highlighted_image)
