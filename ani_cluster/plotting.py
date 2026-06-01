import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def _short_name(path: str) -> str:
        return os.path.splitext(os.path.basename(path))[0]


def plot_ani_heatmap(
        df: pd.DataFrame,
        clusters: list[list[str]],
        representatives: list[str],
        output_html: str,
        threshold: float = 95.0,
) -> None:
        """
        Plot a pairwise ANI heatmap sorted by cluster, with cluster boundary lines
        and representatives marked with * on axis labels.
        Args:
                df (pd.DataFrame): Full fastANI DataFrame (all pairs, unfiltered).
                clusters (list[list[str]]): Clusters as lists of genome identifiers.
                representatives (list[str]): Representative genome per cluster.
                output_html (str): Output HTML file path.
                threshold (float): Clustering threshold; used to center the colorscale.
        Returns:
                None
        """
        if not clusters:
                raise ValueError("Clusters list is empty")
        if len(clusters) != len(representatives):
                raise ValueError("clusters and representatives must have the same length")

        # Build genome order: representative first within each cluster
        rep_set = set(representatives)
        genome_order = []
        boundaries = []
        pos = 0
        for cluster, rep in zip(clusters, representatives):
                ordered = [rep] + [g for g in cluster if g != rep]
                genome_order.extend(ordered)
                pos += len(cluster)
                boundaries.append(pos)
        # keep all cumulative end positions; derive starts for rectangle drawing
        cluster_starts = [0] + boundaries[:-1]
        cluster_ends = boundaries

        n = len(genome_order)
        idx = {g: i for i, g in enumerate(genome_order)}

        # Build ANI matrix — diagonal = 100, off-diagonal filled from df, rest NaN
        matrix = np.full((n, n), np.nan)
        np.fill_diagonal(matrix, 100.0)
        for _, row in df.iterrows():
                q, r, ani = row["query"], row["reference"], row["ani"]
                if q != r and q in idx and r in idx:
                        matrix[idx[q]][idx[r]] = ani

        # Axis labels: short genome names, representatives prefixed with *
        labels = [
                f"* {_short_name(g)}" if g in rep_set else _short_name(g)
                for g in genome_order
        ]

        # Hover text
        hover = [
                [
                        f"Query: {_short_name(genome_order[i])}<br>"
                        f"Ref: {_short_name(genome_order[j])}<br>"
                        f"ANI: {matrix[i][j]:.2f}" if not np.isnan(matrix[i][j]) else
                        f"Query: {_short_name(genome_order[i])}<br>"
                        f"Ref: {_short_name(genome_order[j])}<br>ANI: N/A"
                        for j in range(n)
                ]
                for i in range(n)
        ]

        # Center Viridis colorscale on the clustering threshold
        zmin = max(50.0, 2.0 * threshold - 100.0)
        zmax = 100.0

        fig = go.Figure(go.Heatmap(
                z=matrix,
                x=labels,
                y=labels,
                colorscale="Viridis",
                zmin=zmin,
                zmax=zmax,
                text=hover,
                hoverinfo="text",
                colorbar=dict(title="ANI (%)"),
        ))

        # Outline each cluster's diagonal block with a rectangle
        for start, end in zip(cluster_starts, cluster_ends):
                x0, x1 = start - 0.5, end - 0.5
                fig.add_shape(type="rect", x0=x0, x1=x1, y0=x0, y1=x1,
                              line=dict(color="red", width=2),
                              fillcolor="rgba(0,0,0,0)")

        if n > 200:
                tick_opts = dict(showticklabels=False)
        elif n > 50:
                tick_opts = dict(showticklabels=True, tickfont=dict(size=7))
        else:
                tick_opts = dict(showticklabels=True)

        cell_px = max(4, min(16, 800 // n))
        size = max(500, n * cell_px + 150)

        fig.update_layout(
                title=f"Pairwise ANI Heatmap — clusters sorted, * = representative, threshold = {threshold}%",
                xaxis=dict(**tick_opts, tickangle=45, title="Genome"),
                yaxis=dict(**tick_opts, autorange="reversed", title="Genome"),
                template="plotly_white",
                width=size,
                height=size,
        )

        try:
                fig.write_html(output_html)
        except Exception as e:
                raise RuntimeError(f"Failed to write heatmap to {output_html}: {e}")


def plot_cluster_size_distribution(clusters: list[list[str]], output_html: str) -> None:
        """
        Plot a bar chart of the cluster size distribution.
        Args:
                clusters (list[list[str]]): Clusters as lists of genome identifiers.
                output_html (str): Output HTML file path.
        Returns:
                None
        """
        if not clusters:
                raise ValueError("Clusters list is empty")

        sizes = [len(c) for c in clusters]
        size_counts = (
                pd.Series(sizes, name="size")
                .value_counts()
                .rename_axis("Cluster Size")
                .reset_index(name="Count")
                .sort_values("Cluster Size")
        )

        fig = px.bar(
                size_counts,
                x="Cluster Size",
                y="Count",
                title="Cluster Size Distribution",
                labels={"Cluster Size": "Cluster size (# genomes)", "Count": "Number of clusters"},
                template="plotly_white",
        )
        fig.update_layout(xaxis=dict(dtick=1))

        try:
                fig.write_html(output_html)
        except Exception as e:
                raise RuntimeError(f"Failed to write histogram to {output_html}: {e}")
