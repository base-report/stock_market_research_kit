import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from stock_market_research_kit.average_image import average_images
from utils.cluster_utils import get_all_clusters
from alive_progress import alive_bar


# Folder name
CLUSTERS_FOLDER = "./data/images/clusters/"
AVERAGES_PATH = "./data/images/averages/"


def main():
    clusters = get_all_clusters()
    with alive_bar(len(clusters), title="Averaging clusters") as bar:
        for cluster in clusters:
            images_folder = CLUSTERS_FOLDER + str(cluster)
            output_path = AVERAGES_PATH + str(cluster) + ".png"
            average_images(images_folder, output_path)
            bar()


if __name__ == "__main__":
    main()
