import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import sqlite3
import time
import os
import shutil
from pathlib import Path
from stock_market_research_kit.cluster import get_cluster_assignments
from utils.cluster_utils import get_all_clusters
from alive_progress import alive_bar


DATABASE_PATH = "stock_market_research.db"
N_SUBCLUSTERS = 2
CLUSTERS_FOLDER = "./data/images/clusters/"


def update_subclusters(cluster):
    # Connect to your SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cluster_folder_path = CLUSTERS_FOLDER + str(cluster)
    # Get the ID-label dictionary from the clustering function
    id_label_dict = get_cluster_assignments(cluster_folder_path, N_SUBCLUSTERS)

    # Prepare the list of tuples with label and ID
    update_data = [(int(label), int(id_)) for id_, label in id_label_dict.items()]

    # Update the `trades` table with the subcluster labels in a single transaction
    cursor.executemany("UPDATE trades SET subcluster = ? WHERE id = ?", update_data)

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()


def clear_subcluster_folders(cluster):
    for subcluster in range(N_SUBCLUSTERS):
        subcluster_folder_path = CLUSTERS_FOLDER + str(cluster) + "/" + str(subcluster)
        if os.path.isdir(subcluster_folder_path):
            shutil.rmtree(subcluster_folder_path)


def create_subcluster_folders(cluster):
    for subcluster in range(N_SUBCLUSTERS):
        subcluster_folder = CLUSTERS_FOLDER + str(cluster) + "/" + str(subcluster)

        if not os.path.exists(subcluster_folder):
            os.makedirs(subcluster_folder)


def get_subcluster_data(cursor, cluster):
    cursor.execute("SELECT id, subcluster FROM trades WHERE cluster = ?", (cluster,))
    return {row[0]: row[1] for row in cursor.fetchall()}


def copy_images_to_clusters(cluster):
    clear_subcluster_folders(cluster)

    # Connect to your SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    create_subcluster_folders(cluster)

    subcluster_data = get_subcluster_data(cursor, cluster)

    cluster_folder_path = CLUSTERS_FOLDER + str(cluster)
    for file in os.listdir(cluster_folder_path):
        if file.endswith(".png"):
            file_path = os.path.join(cluster_folder_path, file)
            file_id = int(file.split("__")[-1].split(".")[0])

            # Check if the file_id exists in subcluster_data
            if file_id in subcluster_data:
                cluster_label = subcluster_data[file_id]
                destination_folder = os.path.join(
                    CLUSTERS_FOLDER, str(cluster), str(cluster_label)
                )

                shutil.copy(file_path, destination_folder)


def main():
    clusters = get_all_clusters()
    with alive_bar(len(clusters), title="Subclustering images") as bar:
        for cluster in clusters:
            update_subclusters(cluster)
            copy_images_to_clusters(cluster)
            bar()


if __name__ == "__main__":
    main()
