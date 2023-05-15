from pathlib import Path


# Folder name
CLUSTERS_FOLDER = "./data/images/clusters/"


def get_all_clusters():
    clusters = []

    for cluster in Path(CLUSTERS_FOLDER).iterdir():
        # if not folder, skip
        if not cluster.is_dir():
            continue

        # get the name of the subfolder
        cluster_name = cluster.name

        # append the name to the clusters list
        clusters.append(cluster_name)

    return clusters
