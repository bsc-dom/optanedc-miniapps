from storage.api import StorageObject
from dataclay import dclayMethod

from npp2nvm import np_persist
import numpy as np


class Block(StorageObject):
    """
    @dclayImport numpy as np
    @dclayImportFrom npp2nvm import np_persist
    @ClassField block numpy.array
    """

    @dclayMethod()
    def __init__(self):
        self.block = None

    @dclayMethod(size_x="int", size_y="int")
    def initialize_random(self, size_x, size_y):
        self.block = np.random.random([size_x, size_y])
        #self.block = np_persist(np.random.random([size_x, size_y]))
        #self.block = np.ones([size_x, size_y])

    @dclayMethod(size_x="int", size_y="int")
    def initialize_zeros(self, size_x, size_y):
        # TODO: For matsum, initialize zeros makes no sense.
        # But I already had it (from matmul) and completely missed that.
        # It should be cleaned up, but I am leaving it to be consistent across executions.
        self.block = np.zeros([size_x, size_y])

    @dclayMethod(a="model.block.Block", b="model.block.Block")
    def assign_sum(self, a, b):
        self.block = np_persist(a.block + b.block)
        #self.block = a.block + b.block
