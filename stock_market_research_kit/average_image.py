import numpy as np
import glob
import os
from skimage import io
from skimage import exposure


def increase_contrast_scikit_image(image, gamma=2.3):
    # Adjust gamma to control the level of contrast enhancement
    contrast_image = exposure.adjust_gamma(image, gamma)

    return contrast_image


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

    # Increase the contrast
    contrast_image = increase_contrast_scikit_image(avg_image)

    # Save the averaged image to the output path
    io.imsave(output_path, contrast_image)
