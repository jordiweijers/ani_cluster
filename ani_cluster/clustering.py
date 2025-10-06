import pandas as pd
from collections import defaultdict

def cluster_fastani(df: pd.DataFrame, all_genomes_list: list[str]) -> list[list[str]]:
        """
        Clusters genomes based on high-ANI pairs, but also includes singletons.
        Args:
                df (pd.DataFrame): A DataFrame containing high-ANI pairs
                all_genomes_list (list[str]): A list of all the genomes.
        Returns:
                clusters (list[list[str]]) A list of lists containing all the clusters.
        """
        if df.empty:
                raise ValueError(f"The input DataFrame is empty")
        if not all_genomes_list:
                raise ValueError(f"The list of all genomes is empty")
        try:
                # Create an adjecent dictionary
                adj = defaultdict(set)
                for _, row in df.iterrows():
                        q, r = row["query"], row["reference"]
                        if q != r:
                                adj[q].add(r)
                                adj[r].add(q)
                # Make clusters based on the adjecent dictionary using Depth First Search
                visited = set()
                clusters = []
                for node in adj:
                        if node not in visited:
                                stack = [node]
                                cluster = []
                                while stack:
                                        current = stack.pop()
                                        if current not in visited:
                                                visited.add(current)
                                                cluster.append(current)
                                                stack.extend(adj[current] - visited)
                                clusters.append(cluster)
                # Include singletons
                clustered_genomes = set(g for c in clusters for g in c)
                for g in all_genomes_list:
                        if g not in clustered_genomes:
                                clusters.append([g])
                return clusters
        except Exception as e:
                raise RuntimeError(f"Clustering failed: {e}")

def get_medoid(cluster: list, df: pd.DataFrame) -> str:
        """
        Finds the medoid of a cluster (highest average-ANI)
        Args:
                cluster (list): A list containing all the genomes of a corresponding cluster.
                df (pd.DataFrame): A Pandas DataFrame containing the fastANI output.
        Returns:
                medoid (str): The medoid of a given cluster.
        """
        if not cluster:
                raise ValueError(f"Input cluster is empty")
        if df.empty:
                raise ValueError(f"Input DataFrame is empty")
        try:
                # Return singletons
                if len(cluster) == 1:
                        return cluster[0]
                # Calculate the highest average-ANI
                sub_df = df[df["query"].isin(cluster) & df["reference"].isin(cluster)]
                if sub_df.empty:
                        raise RuntimeError("No ANI pairs found within the cluster. Cannot compute medoid.")
                mean_ani = {g: 0 for g in cluster}
                counts = {g: 0 for g in cluster}
                for _, row in sub_df.iterrows():
                        q, r, ani = row["query"], row["reference"], row["ani"]
                        mean_ani[q] += ani
                        mean_ani[r] += ani
                        counts[q] += 1
                        counts[r] += 1
                avg_ani = {g: mean_ani[g]/counts[g] if counts[g] else 0 for g in cluster}
                return max(avg_ani, key=avg_ani.get)
        except Exception as e:
                raise RuntimeError(f"Medoid calculation failed: {e}")
