import os
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.random_projection import GaussianRandomProjection
from PIL import Image


def get_cluster_assignments(images_folder_path, n_clusters):
    # Get all image files
    image_files = [f for f in os.listdir(images_folder_path) if f.endswith(".png")]

    # Load all images into a numpy array
    images = []
    ids = []
    for file in image_files:
        with Image.open(os.path.join(images_folder_path, file)).convert("L") as im:
            images.append(np.array(im))
            # Extract ID from the file name
            ids.append(int(file.split("__")[1].split(".")[0]))

    # Flatten images
    images = np.array([i.flatten() for i in images])

    # Standardize the data
    scaler = StandardScaler()
    images = scaler.fit_transform(images)

    # Apply random projection before PCA
    reducer = GaussianRandomProjection(n_components=100)
    images_reduced = reducer.fit_transform(images)

    # Apply PCA on the reduced dataset
    pca = PCA(n_components=0.95)
    images = pca.fit_transform(images_reduced)

    # Cluster the data
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(images)

    # Create a dictionary of ID-label pairs
    id_label_dict = {id_: label for id_, label in zip(ids, kmeans.labels_)}

    # Return the ID-label dictionary
    return id_label_dict
