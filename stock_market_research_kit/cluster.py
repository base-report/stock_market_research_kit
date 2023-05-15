import os
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler
import skimage.io
import skimage.transform
from sklearn.preprocessing import normalize


def get_cluster_assignments(images_folder_path, n_clusters):
    # Get all image files
    image_files = [f for f in os.listdir(images_folder_path) if f.endswith(".png")]

    # Load all images into a numpy array
    images = []
    ids = []
    for file in image_files:
        # Read image using scikit-image
        image_path = os.path.join(images_folder_path, file)
        image = skimage.io.imread(image_path)

        # Flatten image into a feature vector
        features = image.flatten()

        # Apply weighting scheme to give more importance to more recent data (right side of the image)
        weight_matrix = np.exp(np.linspace(-3, 0, num=image.shape[1]))
        weighted_features = features * np.tile(weight_matrix, image.shape[0])

        images.append(weighted_features)

        # Extract ID from the file name
        ids.append(int(file.split("__")[1].split(".")[0]))

    # Standardize the data
    images = np.array(images)
    images = normalize(images, axis=1)
    scaler = StandardScaler()
    images = scaler.fit_transform(images)

    # Split the dataset into 20% training and 80% prediction
    training_size = int(0.2 * len(images))
    indices = np.arange(len(images))
    np.random.shuffle(indices)
    training_indices = indices[:training_size]
    prediction_indices = indices[training_size:]

    # Cluster the data
    minibatch_kmeans = MiniBatchKMeans(
        n_clusters=n_clusters, init="k-means++", random_state=0
    )
    minibatch_kmeans.fit(images[training_indices])

    # Predict cluster assignments for the remaining images
    predicted_labels = minibatch_kmeans.predict(images[prediction_indices])

    # Create a dictionary of ID-label pairs
    id_label_dict = {
        id_: label
        for id_, label in zip(
            [ids[i] for i in np.concatenate((training_indices, prediction_indices))],
            np.concatenate((minibatch_kmeans.labels_, predicted_labels)),
        )
    }

    # Return the ID-label dictionary
    return id_label_dict
