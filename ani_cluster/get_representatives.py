import os
import pandas as pd
import logging
from ani_cluster.clustering import cluster_fastani, get_medoid, get_longest
from ani_cluster.plotting import plot_ani_heatmap, plot_cluster_size_distribution

def get_representatives(
        fastani_file: str,
        threshold: float,
        output_file: str,
        cluster_file: str,
        logger: logging.Logger,
        method: str = "medoid",
        heatmap_file: str = None,
        histogram_file: str = None,
) -> tuple:
        """
        Perform dereplication and output representative genomes for each cluster.
        Args:
                fastani_file (str): The path to the fastANI TSV.
                threshold (float): The threshold to use for clustering.
                output_file (str): The output file to write the representative genome list to.
                cluster_file (str): The path to a file to write the cluster membership to (default: None).
                logger (logging.Logger): logger object.
                method (str): Representative selection method: 'medoid' or 'longest' (default: 'medoid').
                heatmap_file (str): If provided, write an ANI heatmap HTML to this path.
                histogram_file (str): If provided, write a cluster size histogram HTML to this path.
        Returns:
                tuple: (representatives list, clusters list)
        """
        if not os.path.isfile(fastani_file):
                raise FileNotFoundError(f"{fastani_file} not found.")
        logger.info(f"Reading fastANI file: {fastani_file}.")
        df = pd.read_csv(fastani_file, sep="\t", header=None)
        df.columns = ["query", "reference", "ani", "frags_aligned", "frags_total"]
        all_genomes = sorted(set(df["query"]).union(df["reference"]))
        filtered_df = df[df["ani"] >= threshold]
        logger.info(f"Clustering genomes with ANI threshold: {threshold}.")
        try:
                clusters = cluster_fastani(filtered_df, all_genomes)
                if method == "longest":
                        logger.info("Selecting representatives by longest genome (frags_total proxy).")
                        representatives = [get_longest(c, df) for c in clusters]
                else:
                        logger.info("Selecting representatives by medoid (highest average ANI).")
                        representatives = [get_medoid(c, filtered_df) for c in clusters]
                logger.info(f"Writing {len(representatives)} representatives to {output_file}.")
                with open(output_file, "w") as f:
                        for r in sorted(representatives):
                                f.write(f"{r}\n")
                if cluster_file:
                        logger.info(f"Writing cluster membership to {cluster_file}.")
                        with open(cluster_file, "w") as f:
                                for rep, cluster in zip(representatives, clusters):
                                        f.write(f"{rep}\t{','.join(cluster)}\n")
                if heatmap_file:
                        logger.info(f"Writing ANI heatmap to {heatmap_file}.")
                        plot_ani_heatmap(df, clusters, representatives, heatmap_file, threshold)
                if histogram_file:
                        logger.info(f"Writing cluster size histogram to {histogram_file}.")
                        plot_cluster_size_distribution(clusters, histogram_file)
                logger.info("Dereplication completed successfully.")
                return representatives, clusters
        except Exception as e:
                logger.error(f"Failed to get representatives: {e}")
                raise RuntimeError(f"get_representatives failed: {e}")
