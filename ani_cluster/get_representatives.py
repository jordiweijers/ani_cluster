import os
import pandas as pd
import logging
from ani_cluster.clustering import cluster_fastani, get_medoid

def get_representatives(fastani_file: str, threshold: float, output_file: str, cluster_file: str, logger: logging.Logger) -> None:
        """
        Perform dereplication and output medoid genomes as representatives of each cluster.
        Args:
                fastani_file (str): The path to the fastANI TSV.
                threshold (float): The thresholds to use for clustering.
                output_file (str): The output file to write the representative genome list to.
                cluster_file (str): The path to a file to write the cluster membership to (default: None).
                logger (logging.Logger): logger object.
        Returns:
                None
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
                medoids = [get_medoid(c, filtered_df) for c in clusters]
                logger.info(f"Writing {len(medoids)} medoids to {output_file}.")
                with open(output_file, "w") as f:
                        for m in sorted(medoids):
                                f.write(f"{m}\n")
                if cluster_file:
                        logger.info(f"Writing cluster membership to {cluster_file}.")
                        with open(cluster_file, "w") as f:
                                for medoid, cluster in zip(medoids, clusters):
                                        f.write(f"{medoid}\t{','.join(cluster)}\n")
                logger.info("Dereplication completed successfully.")
                return medoids, clusters
        except Exception as e:
                logger.error(f"Failed to get representatives: {e}")
                raise RuntimeError(f"get_representatives failed: {e}")
