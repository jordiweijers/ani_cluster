import os
import numpy as np
import pandas as pd
import plotly.express as px
import logging
from ani_cluster.clustering import cluster_fastani

def plot_thresholds_vs_clusters(thresholds: list[float], num_clusters: list[int], output_html: str) -> None:
        """
        Create an interactive thresholds vs clusters HTML plot.
        Args:
                thresholds (list[float]): A list of thresholds.
                num_clusters (list[int]): A list of number of clusters.
                output_html (str): The path to save to HTML plot to.
        Returns:
                None
        """
        if not thresholds:
                raise ValueError("Thresholds list is empty")
        if not num_clusters:
                raise ValueError("Number of clusters list is emtpy")
        try:
                df = pd.DataFrame({
                        "ANI Threshold": thresholds,
                        "Number of Clusters": num_clusters
                })
                fig = px.line(
                        df,
                        x="ANI Threshold",
                        y="Number of Clusters",
                        markers=True,
                        title="ANI Thresholds vs Number of Clusters"
                )
                fig.update_traces(mode="lines+markers")
                fig.update_layout(
                        xaxis_title="ANI Thresholds (%)",
                        yaxis_title="Number of clusters (n)",
                        template="plotly_white"
                )
                fig.write_html(output_html)
        except Exception as e:
                raise RuntimeError(f"Failed to create or save the plot to {output_html}: {e}")

def determine_threshold(fastani_file: str, output_plot: str, start: float, end: float, step: float, logger: logging.Logger) -> None:
        """
        Run clustering over a range of thresholds and plot numbers of clusters against thresholds.
        Args:
                fastani_file (str): The path to the fastANI TSV.
                output_plot (str): The path to save the HTML output.
                start (float): The bottom threshold to test.
                end (float): The top threshold to test.
                step (float): How big of steps to take for the thresholds.
                logger (logging.Logger): logger object.
        Returns:
                None
        """
        if not os.path.isfile(fastani_file):
                raise FileNotFoundError(f"{fastani_file} not found.")
        logger.info(f"Reading fastANI file: {fastani_file}")
        df = pd.read_csv(fastani_file, sep="\t", header=None)
        df.columns = ["query", "reference", "ani", "frags_aligned", "frags_total"]
        all_genomes = sorted(set(df["query"]).union(df["reference"]))
        thresholds = np.arange(start, end + step / 2, step)
        num_clusters = []
        logger.info(f"Caculating clusters for thresholds from {start} to {end} (step={step}).")
        try:
                for t in thresholds:
                        filtered_df = df[df["ani"] >= t]
                        clusters = cluster_fastani(filtered_df, all_genomes)
                        num_clusters.append(len(clusters))
                logger.info(f"Creating HTML plot: {output_plot}")
                plot_thresholds_vs_clusters(thresholds.tolist(), num_clusters, output_plot)
        except Exception as e:
                logger.error(f"Failed to determine thresholds: {e}")
                raise RuntimeError(f"determine_thresholds failed: {e}")
