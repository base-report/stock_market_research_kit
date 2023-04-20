import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import sqlite3
import time
import os
import shutil
from pathlib import Path
from stock_market_research_kit.cluster import get_cluster_assignments


DATABASE_PATH = "stock_market_research.db"
N_CLUSTERS = 5
FOLDER_PATH = "./data/images"

images_folder_path = FOLDER_PATH + "/all"
clusters_folder_path = FOLDER_PATH + "/clusters"


def update_clusters():
    # Get the ID-label dictionary from the clustering function
    id_label_dict = get_cluster_assignments(images_folder_path, N_CLUSTERS)

    # Connect to your SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Prepare the list of tuples with label and ID
    update_data = [(int(label), int(id_)) for id_, label in id_label_dict.items()]

    # Update the `trades` table with the cluster labels in a single transaction
    cursor.executemany("UPDATE trades SET cluster = ? WHERE id = ?", update_data)

    cursor.execute(
        "SELECT id, symbol, entry_date, cluster, CAST(cluster AS TEXT) as cluster_text FROM trades WHERE cluster = 1 LIMIT 10;"
    )

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()


def clear_cluster_folders():
    for folder in os.listdir(clusters_folder_path):
        folder_path = os.path.join(clusters_folder_path, folder)
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)


def create_cluster_folders(n_clusters):
    for i in range(n_clusters):
        cluster_folder = os.path.join(clusters_folder_path, str(i))
        if not os.path.exists(cluster_folder):
            os.makedirs(cluster_folder)


def get_cluster_data(cursor):
    cursor.execute("SELECT id, cluster FROM trades")
    return {row[0]: row[1] for row in cursor.fetchall()}


def copy_images_to_clusters():
    # Clear existing cluster folders
    clear_cluster_folders()

    # Connect to your SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get the number of clusters from the trades table
    cursor.execute("SELECT DISTINCT cluster FROM trades")
    n_clusters = len(cursor.fetchall())

    # Create new cluster folders
    create_cluster_folders(n_clusters)

    # Get cluster data
    cluster_data = get_cluster_data(cursor)

    for file in os.listdir(images_folder_path):
        if file.endswith(".png"):
            file_path = os.path.join(images_folder_path, file)
            file_id = int(file.split("__")[-1].split(".")[0])

            # Check if the file_id exists in cluster_data
            if file_id in cluster_data:
                cluster_label = cluster_data[file_id]
                destination_folder = os.path.join(
                    clusters_folder_path, str(cluster_label)
                )
                shutil.copy(file_path, destination_folder)


def main():
    print("Clustering images (this may take a while) ...")
    time_before = time.time()

    update_clusters()
    copy_images_to_clusters()

    time_taken = time.time() - time_before
    print(f"Time taken: {time_taken} seconds")


if __name__ == "__main__":
    main()
