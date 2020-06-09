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
        #self.block = np.random.random([size_x, size_y])
        self.block = np_persist(np.random.random([size_x, size_y]))
        #self.block = np.ones([size_x, size_y])

    @dclayMethod(size_x="int", size_y="int")
    def initialize_zeros(self, size_x, size_y):
        self.block = np_persist(np.zeros([size_x, size_y]))
        #self.block = np.zeros([size_x, size_y])

    @dclayMethod(a="model.block.Block", b="model.block.Block")
    def mul_n_isum(self, a, b):
        self.block += a.block @ b.block

    @dclayMethod()
    def persist(self):
        self.block = np_persist(self.block)
