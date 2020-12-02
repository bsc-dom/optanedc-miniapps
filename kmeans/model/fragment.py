from dataclay import DataClayObject, dclayMethod

import numpy as np
from npp2nvm import np_persist
from sklearn.metrics import pairwise_distances


class Fragment(DataClayObject):
    """
    @ClassField points numpy.ndarray

    @dclayImport numpy as np
    @dclayImportFrom npp2nvm import np_persist
    @dclayImportFrom sklearn.metrics import pairwise_distances
    """
    @dclayMethod()
    def __init__(self):
        self.points = None

    @dclayMethod(centers='numpy.ndarray', return_='anything')
    def partial_sum(self, centers):
        partials = np.zeros((centers.shape[0], 2), dtype=object)
        ## Use the copy to evaluate AD (pre-copy) scenario:
        # arr = self.points.copy()
        ## Use this for all the remaining active scenarios:
        arr = self.points
        close_centers = pairwise_distances(arr, centers).argmin(axis=1)
        for center_idx in range(len(centers)):
            indices = np.argwhere(close_centers == center_idx).flatten()
            partials[center_idx][0] = np.sum(arr[indices], axis=0)
            partials[center_idx][1] = indices.shape[0]
        
        return partials

    @dclayMethod(num_points='int', dim='int', mode='str', seed='int')
    def generate_points(self, num_points, dim, mode, seed):
        """
        Generate a random fragment of the specified number of points using the
        specified mode and the specified seed. Note that the generation is
        distributed (the master will never see the actual points).
        :param num_points: Number of points
        :param dim: Number of dimensions
        :param mode: Dataset generation mode
        :param seed: Random seed
        :return: Dataset fragment
        """
        # Random generation distributions
        rand = {
            'normal': lambda k: np.random.normal(0, 1, k),
            'uniform': lambda k: np.random.random(k),
        }
        r = rand[mode]
        np.random.seed(seed)
        mat = np.array(
            [r(dim) for __ in range(num_points)]
        )
        # Normalize all points between 0 and 1
        mat -= np.min(mat)
        mx = np.max(mat)
        if mx > 0.0:
            mat /= mx

        self.points = mat

    @dclayMethod()
    def persist_to_nvram(self):
        self.points = np_persist(self.points)
