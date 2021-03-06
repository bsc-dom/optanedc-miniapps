from dataclay import DataClayObject, dclayMethod


import numpy as np
from npp2nvm import np_persist


class Fragment(DataClayObject):
    """
    @ClassField values numpy.ndarray

    @dclayImport numpy as np
    @dclayImportFrom npp2nvm import np_persist
    """
    @dclayMethod()
    def __init__(self):
        self.values = None

    @dclayMethod(num_values='int', seed='int')
    def generate_values(self, num_values, seed):
        """Generate values following a certain distribution.

        :param num_values: Number of points
        :param distribution_func_name: The numpy.random's name for the distribution that 
         will be used to generate the values.
        :param seed: Random seed
        :return: Dataset fragment
        """
        # Random generation distributions
        np.random.seed(seed)
        values = np.random.f(10, 2, num_values)

        self.values = values

    @dclayMethod()
    def persist_to_nvram(self):
        self.values = np_persist(self.values)

    @dclayMethod(bins="numpy.ndarray", return_="numpy.ndarray")
    def partial_histogram(self, bins):
        values, _ = np.histogram(self.values, bins)
        return values
