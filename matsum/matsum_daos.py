"""Simple adaptation of matsum to PyDAOS.

The matsum.py (containing a Matrix Addition done with the dataClay
framework) is used as the reference implementation. Naming and structures have
been adapted to make sense with PyDAOS.

For details and more documentation, check that reference implementation instead
of this.
"""

from __future__ import print_function

import time
import os
import sys
import operator

import numpy as np
import pydaos


#############################################
# Constants / experiment values:
#############################################

BLOCKSIZE = 4096
MATRIXSIZE = 14

DAOS_POOL_UUID = os.environ["DAOS_POOL"]
DAOS_CONT_UUID = os.environ["DAOS_CONT"]

#############################################
#############################################

DAOS_CONT = pydaos.Cont(DAOS_POOL_UUID, DAOS_CONT_UUID)
DAOS_KV = DAOS_CONT.rootkv()

NP_FROMSTRING_DTYPE = np.dtype('float64')

class ResultMatrixInMemory:
    def __init__(self):
        self.blocks = dict()

    def __setitem__(self, key, value):
        self.blocks[key] = value

    def __getitem__(self, key):
        return self.blocks[key]


class ResultMatrixInDaos:
    def __init__(self):
        pass

    def __setitem__(self, key, value):
        i, j = key
        DAOS_KV["C%02d%02d" % (i, j)] = value.tostring()

    def __getitem__(self, key):
        i, j = key 
        return np.fromstring(
            DAOS_KV["C%02d%02d" % (i, j)],
            dtype=NP_FROMSTRING_DTYPE
        ).reshape((BLOCKSIZE, BLOCKSIZE))


def matsum():
    """Multiply A * B, return resulting C."""

    matrix_c = ResultMatrixInMemory()
    # matrix_c = ResultMatrixInDaos()

    for i in range(MATRIXSIZE):
        for j in range(MATRIXSIZE):
            print("Evaluating output cell (%d, %d)" % (i, j))

            a_block = np.fromstring(
                DAOS_KV["A%02d%02d" % (i, j)],
                dtype=NP_FROMSTRING_DTYPE
            ).reshape((BLOCKSIZE, BLOCKSIZE))

            b_block = np.fromstring(
                DAOS_KV["A%02d%02d" % (i, j)],
                dtype=NP_FROMSTRING_DTYPE
            ).reshape((BLOCKSIZE, BLOCKSIZE))
            
            matrix_c[i,j] = a_block + b_block

    return matrix_c


def prepare_block(name, coord_i, coord_j):
    """Create a persistent block or retrieve it."""
    alias = "%s%02d%02d" % (name, coord_i, coord_j)

    block = np.random.random((BLOCKSIZE, BLOCKSIZE))

    DAOS_KV[alias] = block.tostring()


def main():

    print("""Starting experiment with the following:

BLOCKSIZE = {blocksize}
MATRIXSIZE = {matrixsize}
""".format(blocksize=BLOCKSIZE,
           matrixsize=MATRIXSIZE)
    )

    start_time = time.time()

    print("Preparing B")
    _ = [[prepare_block("B", i, j) for i in range(MATRIXSIZE)] for j in range(MATRIXSIZE)]
    print("Preparing A")
    _ = [[prepare_block("A", i, j) for i in range(MATRIXSIZE)] for j in range(MATRIXSIZE)]
 
    print("Generation/Load done")
    initialization_time = time.time()
    print("Starting matsum")

    # Run matsum
    matrix_c = matsum()

    print("Ending matsum")

    matmul_time = time.time()

    # print("Second round of matsum")
    # matrix_c = matsum()

    # print("Ending matsum")
    # matmul_2nd = time.time()

    print("-----------------------------------------")
    print("-------------- RESULTS ------------------")
    print("-----------------------------------------")
    print("Initialization time: %f" % (initialization_time - start_time))
    print("Matsum time: %f" % (matmul_time - initialization_time))
    # print("Matmul 2nd round time: %f" % (matmul_2nd - matmul_time))
    # print("Total time: %f" % (matmul_2nd - start_time))
    print("-----------------------------------------")


if __name__ == "__main__":
    main()
