# ANI Cluster

`ani_cluster` is a Python tool to cluster genomes based on Average Nucleotide Identity (ANI) scores.  
It can determine optimal clustering thresholds and select representative genomes (medoids) from clusters, providing a non-redundant genome set.

## Features

- Determine optimal ANI thresholds for clustering genomes
- Cluster genomes based on ANI scores
- Select representative genomes (medoids) from each cluster
- Interactive HTML plots for threshold vs. number of clusters
- Command-line interface for easy usage

## Installation

Clone the repository and install via pip:

```bash
git clone https://github.com/yourusername/ani_cluster.git
cd ani_cluster
pip install .
```
All required dependencies are listed in `requirements.txt` and will be installed automatically.

## Usage

`ani_cluster` provides two main modes:

### 1. Determine optimal ANI threshold
This mode calculates the number of clusters for a range of ANI thresholds and generates an interactive HTML plot to help identify the best threshold.

```bash
usage: ani_cluster determine_threshold [-h] -a ANI [-o OUTPUT] -t START END STEP

  -h, --help            show this help message and exit
  -a ANI, --ani ANI     all-vs-all fastANI output TSV file.
  -o OUTPUT, --output OUTPUT
                        Output plot file name (default: thresholds_vs_clusters.html).
  -t START END STEP, --thresholds START END STEP
                        Range of ANI thresholds to test: START END STEP (e.g. 90 99 0.5)
```

### 2. Get representative genomes (medoids)
This mode clusters genomes using a specified ANI threshold and selects one representative genome (medoid) from each cluster. It outputs a non-redundant list of genomes and optionally a file showing cluster membership.

```bash
usage: ani_cluster get_representatives [-h] -a ANI -t THRESHOLD -o OUTPUT [-c CLUSTER_MEMBERSHIP]

  -h, --help            show this help message and exit
  -a ANI, --ani ANI     all-vs-all fastANI output TSV file.
  -t THRESHOLD, --threshold THRESHOLD
                        ANI threshold for clustering
  -o OUTPUT, --output OUTPUT
                        Output file for representative (medoid) genome list.
  -c CLUSTER_MEMBERSHIP, --cluster_membership CLUSTER_MEMBERSHIP
                        Cluster membership file (Optional).
```
