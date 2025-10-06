from setuptools import setup, find_packages

VERSION = "0.1.0"
DESCRIPTION = "ANI cluster helps you to determine thresholds for clustering genomes based on their ANI scores. It also is able to pick representatives of these clusters to give you a list of nonredundant genomes. It does this based on the highest average ANI score (medoid) of a cluster."

with open("requirements.txt") as f:
		requirements = f.read().splitlines()

setup(
	name="ani_cluster",
	version=VERSION,
	author="Jordi Weijers",
	author_email="jweijers@ifam.uni-kiel.de",
	description=DESCRIPTION,
	packages=find_packages(),
	install_requires=requirements,
	entry_points={'console_scripts': ["ani_cluster=ani_cluster.main:main"]}
)
