import os
import itertools
import random
import sys
from colorama import Fore, Back, Style
from time import perf_counter

import numpy as np
from sklearn.cluster import AffinityPropagation, SpectralClustering, DBSCAN

from qgram import getProfiles, cosQgramDistance


class Cluster:
    """
    A cluster data structure, consisting of a reference of the whole dataset
    (`self.dataset`), the indices of the elements in the cluster (`self.items`)
    and the exemplar (`self.exemplar`) if there's one.

    In order to get elements in the cluster, you can simply iterate 
    `cluster.items` to get the indices, and then use `cluster.dataset[index]` 
    to get the element.
    """
    def __init__(self, items, dataset, exemplar=None):
        self.items = items
        self.dataset = dataset
        self.exemplar = exemplar
        self.max_dist = 0
        self.updateProfiles()

    def append(self, index):
        self.items.append(index)
        self.profiles.append(getProfiles(self.dataset[index]))
        
    def extend(self, cluster):
        self.items.extend(cluster.items)
        self.profiles.extend(cluster.profiles)

    def delete(self, index):
        pos = self.items.index(index)
        del self.items[pos]
        del self.profiles[pos]

    def updateProfiles(self):
        self.profiles = [getProfiles(self.dataset[item]) for item in self.items]

    def updateMaxDist(self, dist_func, k=8):
        samples = random.sample(self.items, min(k, len(self)))
        dist_matrix = np.array([[dist_func(self.dataset[l1], self.dataset[l2]) 
                                 for l1 in samples] for l2 in samples])
        self.max_dist = max(self.max_dist, np.max(dist_matrix))

    def distanceToData(self, profile, dist_func, k=8):
        samples = random.sample(self.profiles, min(k, len(self)))
        dist = np.array([dist_func(profile, sample) for sample in samples])
        return np.min(dist), np.mean(dist), np.max(dist)

    def distanceToCluster(self, cluster, dist_func, k=8):
        samples1 = random.sample(self.profiles, min(k, len(self)))
        samples2 = random.sample(cluster.profiles, min(k, len(cluster)))
        dist = np.array([[dist_func(s1, s2) for s2 in samples2] for s1 in samples1])
        return np.min(dist), np.mean(dist), np.max(dist)

    def printData(self, file=sys.stdout, highlight=True):
        for item_id in self.items:
            item = self.dataset[item_id]
            if highlight and self.exemplar is not None:
                if item_id == self.exemplar:
                    print(f"{Fore.MAGENTA}{Back.LIGHTCYAN_EX}[{item_id}]{item}{Style.RESET_ALL}", file=file)
                else:
                    print(f"[{item_id}]{item}", file=file)
            else:
                print(f"[{item_id}]{item}", file=file)
        
        print(file=file)
    
    def getData(self):
        logset = []
        for item_id in self.items:
            item = self.dataset[item_id]
            logset.append((item_id, item))
        return logset

    def getDataset(self):
        return self.dataset

    def __repr__(self):
        # return f"{Fore.MAGENTA}{Back.LIGHTCYAN_EX}" \
        #        f"<Cluster (size {len(self)}, max_dist {self.max_dist})>" \
        #        f"{Style.RESET_ALL}: {self.items}"
        return f"<Cluster (size {len(self)}, max_dist {self.max_dist})>: {self.items}"
    
    def __len__(self):
        return len(self.items)
    
    def __bool__(self):
        return bool(len(self))
    
    def __iter__(self):
        return (x for x in zip(self.items, self.profiles))


def clustering(data, dist_func, dataset, method="AffinityPropagation", **kwargs):
    """Core clustering function

    Use models in `sklearn` to perform clustering. `AffinityPropagation`, 
    `SpectralClustering`, `DBSCAN` are supported.

    Parameters:
    :param `data`: a list of input data
    :param `dist_func`: a function used to calculate distance
    :param `dataset`: a reference of the dataset
    :param `method`: model type (string)
    :param `**kwargs`: other parameters used to initialize the model

    Return a tuple `(model, clusters)`. `model` is the sklearn model. `clusters`
    is a list of `Cluster` objects, each of which stands for a cluster.
    """

    # Calculate distance matrix
    # dist_matrix = np.array([[dist_func(l1, l2) for l1 in data] for l2 in tqdm(data)])  # time-consuming
    dist_matrix = np.array([[dist_func(l1, l2) for l1 in data] for l2 in data])  # time-consuming

    # Fill the diagonal (`diagonal` in kwargs, default np.median)
    diagonal_func = kwargs.get("diagonal", np.median)
    if callable(diagonal_func):
        np.fill_diagonal(dist_matrix, diagonal_func(dist_matrix))
    else:
        np.fill_diagonal(dist_matrix, diagonal_func)
    if "diagonal" in kwargs:
        del kwargs["diagonal"]

    # Normalize data (`normalized` in kwargs)
    if kwargs.get("normalized"):
        del kwargs["normalized"]
        maximum = np.max(dist_matrix)
        minimum = np.min(dist_matrix)
        diff = maximum - minimum
        dist_matrix = (dist_matrix - minimum) / diff

    # print(dist_matrix)

    # Affinity matrix
    aff_matrix = np.max(dist_matrix) - dist_matrix

    if method == "AffinityPropagation":
        # Apply Affinity Propagation
        model = AffinityPropagation(affinity="precomputed", **kwargs)
        model.fit(aff_matrix)
        clusters = {exemplar_id: list() for exemplar_id in model.cluster_centers_indices_}
        for i, cluster_id in enumerate(model.labels_):
            clusters[model.cluster_centers_indices_[cluster_id]].append(i)
        clusters = [Cluster(cluster, dataset, ex) for ex, cluster in clusters.items()]

    elif method == "SpectralClustering":
        # Apply Spectral Clustering
        os.environ["OMP_NUM_THREADS"] = "1"
        model = SpectralClustering(affinity="precomputed", **kwargs)
        model.fit(aff_matrix)
        clusters = [list() for _ in np.unique(model.labels_)]
        for i, cluster_id in enumerate(model.labels_):
            clusters[cluster_id].append(i)
        clusters = [Cluster(cluster, dataset) for cluster in clusters]

    elif method == "DBSCAN":
        # Apply DBSCAN clustering
        model = DBSCAN(metric="precomputed", **kwargs)
        model.fit(dist_matrix)
        clusters = [list() for _ in np.unique(model.labels_)]
        for i, cluster_id in enumerate(model.labels_):
            clusters[cluster_id].append(i)
        clusters = [Cluster(cluster, dataset) for cluster in clusters]

    else:
        raise SyntaxError(f"Method {method} not supported")
    
    # Save affinity and max_dist data info `cluster` objects
    for cluster in clusters:
        items = np.array(cluster.items)
        # aff = aff_matrix[np.ix_(items, items)]
        # np.fill_diagonal(aff, 0)
        # cluster.min_affinity = np.min(aff)
        dist = dist_matrix[np.ix_(items, items)]
        np.fill_diagonal(dist, 0)
        cluster.max_dist = np.max(dist)
        # print(dist)

    return model, clusters


def showClusters(result, file=sys.stdout, highlight=True):
    """Print the clusters into `file`.

    Parameters:
    :param `result`: a list of `cluster` objects
    :param `file`: an IO instance (default sys.stdout)
    :param `highlight`: whether to show the exemplar in the cluster (boolean)
    """
    for i, cluster in enumerate(result):
        if cluster:
            print(f"Cluster {i}:", file=file)
            cluster.printData(file, highlight)

def get_clusters_log(input_path, LIMIT=100):
    method = {
        "diagonal": np.median,
        # "method": "AffinityPropagation",
        # "damping": 0.5,
        "method": "SpectralClustering",
        "n_clusters": 20,
        # "method": "DBSCAN",
        # "eps": 0.2,
        # "normalized": True
    }

    new_log_index = []
    new_log_set = []

    with open(input_path, "r", encoding='utf-8') as handle:
        # t = perf_counter()
        while (True):
            limit = itertools.takewhile(lambda n: n < LIMIT, itertools.count())
            lines = zip(limit, handle)
            lines = [line.strip() for _, line in lines]
            if (len(lines) == 0):
                break

            profiles = [getProfiles(line) for line in lines]

            model, clusters = clustering(profiles, cosQgramDistance, lines, **method)
            # print(clusters)
            # showClusters(clusters)
            for cluster in clusters:
                logset = cluster.getData()
                # print(logset)
                for log in logset:
                    new_log_index.append(log[0])
                    new_log_set.append(log[1])

        # print(new_log_index)
        # print(new_log_set)
        # print(len(new_log_set))
        # t = perf_counter() - t
        # print("cluster time", t)

        return new_log_index, new_log_set


if __name__ == "__main__":
    input_path = "./datasets/test1_data_size/Linux_10000.txt"
    log_index, log_set = get_clusters_log(input_path)
    # print(log_index)
    print(len(log_set))
    
