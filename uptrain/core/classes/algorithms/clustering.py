import numpy as np
from uptrain.core.lib.helper_funcs import cluster_and_plot_data

class Clustering():
    def __init__(self, args) -> None:
        self.NUM_BUCKETS = args["num_buckets"]
        self.is_embedding = args["is_embedding"]
        self.plot_save_name = args.get("plot_save_name", "")
        self.cluster_plot_func = args.get('cluster_plot_func', None)
        self.dist = []
        self.dist_counts = []
        self.max_along_axis = []


    def cluster_data(self, data):
        if self.is_embedding:
            self.bucket_vector(data)
        else:
            buckets = []
            clusters = []
            cluster_vars = []
            for idx in range(data.shape[1]):
                this_inputs = data[:, idx]
                this_buckets, this_clusters, this_cluster_vars = self.bucket_scalar(
                    this_inputs
                )
                buckets.append(this_buckets)
                clusters.append(this_clusters)
                cluster_vars.append(this_cluster_vars)
            self.buckets = np.array(buckets)
            self.clusters = np.array(clusters)
            self.cluster_vars = np.array(cluster_vars)

        self.dist = np.array(self.dist)
        self.dist_counts = np.array(self.dist_counts)

        clustering_results = {
            "buckets": self.buckets,
            "clusters": self.clusters,
            "cluster_vars": self.cluster_vars,
            "dist": self.dist,
            "dist_counts": self.dist_counts,
            "max_along_axis": self.max_along_axis
        }

        return clustering_results


    def bucket_scalar(self, arr):
        if isinstance(arr[0], str):
            uniques, counts = np.unique(np.array(arr), return_counts=True)
            buckets = uniques
            self.NUM_BUCKETS = len(buckets)
            clusters = uniques
            cluster_vars = [None] * self.NUM_BUCKETS
            self.ref_dist.append([[counts[x] / len(arr)] for x in range(self.NUM_BUCKETS)])
            self.ref_dist_counts.append(
                [[counts[x]] for x in range(self.NUM_BUCKETS)]
            )
        else:
            sorted_arr = np.sort(arr)
            buckets = []
            clusters = []
            cluster_vars = []
            for idx in range(0, self.NUM_BUCKETS):
                if idx > 0:
                    buckets.append(
                        sorted_arr[int(idx * (len(sorted_arr) - 1) / self.NUM_BUCKETS)]
                    )
                this_bucket_elems = sorted_arr[
                    int((idx) * (len(sorted_arr) - 1) / self.NUM_BUCKETS) : int(
                        (idx + 1) * (len(sorted_arr) - 1) / self.NUM_BUCKETS
                    )
                ]
                gaussian_mean = np.mean(this_bucket_elems)
                gaussian_var = np.var(this_bucket_elems)
                clusters.append([gaussian_mean])
                cluster_vars.append([gaussian_var])

        self.dist.append([[1 / self.NUM_BUCKETS] for x in range(self.NUM_BUCKETS)])
        self.dist_counts.append(
            [[int(len(sorted_arr) / self.NUM_BUCKETS)] for x in range(self.NUM_BUCKETS)]
        )
        return np.array(buckets), np.array(clusters), np.array(cluster_vars)

    def bucket_vector(self, data):

        abs_data = np.abs(data)
        self.max_along_axis = np.max(abs_data, axis=0)
        data = data/self.max_along_axis

        all_clusters, counts, cluster_vars = cluster_and_plot_data(
            data,
            self.NUM_BUCKETS,
            cluster_plot_func=self.cluster_plot_func,
            plot_save_name=self.plot_save_name,
        )

        self.clusters = np.array([all_clusters])
        self.cluster_vars = np.array([cluster_vars])
        self.buckets = self.clusters

        self.dist_counts = np.array([counts])
        self.dist = self.dist_counts / data.shape[0]

    def infer_cluster_assignment(self, feats, prod_dist_counts=None):
        if prod_dist_counts is None:
            prod_dist_counts = np.zeros((feats.shape[1], self.NUM_BUCKETS))
        if self.is_embedding:
            selected_cluster = np.argmin(
                np.sum(
                    np.abs(self.clusters[0] - feats),
                    axis=tuple(range(2, len(feats.shape))),
                ),
                axis=1,
            )
            for clus in selected_cluster:
                prod_dist_counts[0][clus] += 1
            this_datapoint_cluster = selected_cluster
        else:
            this_datapoint_cluster = []
            for idx in range(feats.shape[2]):
                if isinstance(feats[0,0,idx], str):
                    try:
                        bucket_idx = np.array([
                            list(self.buckets[idx]).index(feats[x,0,idx]) for x in range(feats.shape[0])
                        ])
                    except:
                        # TODO: This logic is not completely tested yet. Contact us if you are facing issues
                        # If given data-point is not present -> add a new bucket
                        temp_buckets = list(self.buckets[idx])
                        num_added = 0

                        for x in range(feats.shape[0]):
                            if feats[x,0,idx] not in temp_buckets:
                                temp_buckets.append(feats[x,0,idx])
                                num_added += 1
                        
                        self.buckets[idx] = np.array(temp_buckets)
                        bucket_idx = np.array([
                            list(self.buckets[idx]).index(feats[x,0,idx]) for x in range(feats.shape[0])
                        ])
                else:
                    bucket_idx = np.searchsorted(
                        self.buckets[idx], feats[:, :, idx]
                    )[:, 0]
                this_datapoint_cluster.append(bucket_idx)
                for clus in bucket_idx:
                    prod_dist_counts[idx][clus] += 1
            this_datapoint_cluster = np.array(this_datapoint_cluster)
        return this_datapoint_cluster, prod_dist_counts