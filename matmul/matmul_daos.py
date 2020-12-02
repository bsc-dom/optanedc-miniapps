"""Simple adaptation of matmul to PyDAOS.

The matmul.py (containing a Matrix Multiplication done with the dataClay
framework) is used as the reference implementation. Naming and structures have
been adapted to make sense with PyDAOS.

For details and more documentation, check that reference implementation instead
of this.
"""

from __future__ import print_function

import time
import os
import sys
import gc

import numpy as np
import pydaos


#############################################
# Constants / experiment values:
#############################################

BLOCKSIZE = int(os.environ["BLOCKSIZE"])
MATRIXSIZE = int(os.environ["MATRIXSIZE"])
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "10"))
RESULT_IN_NVRAM = bool(int(os.getenv("RESULT_IN_NVRAM", "0")))


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


def matmul():
    """Eval A * B, return resulting C."""

    if RESULT_IN_NVRAM:
        matrix_c = ResultMatrixInDaos()
    else:
        matrix_c = ResultMatrixInMemory()

    # This could be trivially optimized by reordering indexes
    # and caching either a_block or b_block (assuming C in-memory).
    # *However* it would result in unfair comparisons with the 
    # previous implementation used elsewhere.
    # Using the naive algorithm makes sense for a raw comparison.
    for i in range(MATRIXSIZE):
        for j in range(MATRIXSIZE):
            partial_result_block = np.zeros((BLOCKSIZE, BLOCKSIZE))

            for k in range(MATRIXSIZE):
                a_block = np.fromstring(
                    DAOS_KV["A%02d%02d" % (i, k)],
                    dtype=NP_FROMSTRING_DTYPE
                ).reshape((BLOCKSIZE, BLOCKSIZE))

                b_block = np.fromstring(
                    DAOS_KV["B%02d%02d" % (k, j)],
                    dtype=NP_FROMSTRING_DTYPE
                ).reshape((BLOCKSIZE, BLOCKSIZE))

                partial_result_block += a_block @ b_block
            
            matrix_c[i,j] = partial_result_block

    return matrix_c


def prepare_block(name, coord_i, coord_j):
    """Create a persistent block or retrieve it."""
    alias = "%s%02d%02d" % (name, coord_i, coord_j)

    block = np.random.random((BLOCKSIZE, BLOCKSIZE))

    DAOS_KV[alias] = block.tostring()


def main():

    print(f"""Starting experiment with the following:

BLOCKSIZE = {BLOCKSIZE}
MATRIXSIZE = {MATRIXSIZE}
NUMBER_OF_ITERATIONS = {NUMBER_OF_ITERATIONS}
RESULT_IN_NVRAM = {RESULT_IN_NVRAM}
""")

    start_time = time.time()

    print("Preparing B")
    _ = [[prepare_block("B", i, j) for i in range(MATRIXSIZE)] for j in range(MATRIXSIZE)]
    print("Preparing A")
    _ = [[prepare_block("A", i, j) for i in range(MATRIXSIZE)] for j in range(MATRIXSIZE)]
 
    print("Generation/Load done")
    initialization_time = time.time()
    print("Starting matmul")

    print("-----------------------------------------")
    print("-------------- RESULTS ------------------")
    print("-----------------------------------------")
    print("Initialization time: %f" % (initialization_time - start_time))

    result_times = list()

    # Run matmul
    for i in range(NUMBER_OF_ITERATIONS):
        start_t = time.time()
        matrix_c = matmul()
        end_t = time.time()

        matmul_time = end_t - start_t
        print("Matmul time (#%d/%d): %f" % (i + 1, NUMBER_OF_ITERATIONS, matmul_time))

        result_times.append(matmul_time)

        # Cleanup matrix_c
        if not RESULT_IN_NVRAM:
            del matrix_c.blocks
            gc.collect()
            # this is required when RESULT_IN_NVRAM is False as app was crashing 
            # presumably, it was an out of memory

    print("-----------------------------------------")

    with open("results_daos.csv", "a") as f:
        for result in result_times:
            # Mangling everything with a ",".join
            content = ",".join([
                str(BLOCKSIZE),
                str(MATRIXSIZE),
                "1",  # INPUT_IN_NVRAM is always 1, it does not make sense otherwise
                str(int(RESULT_IN_NVRAM)),
                "DAOS",
                str(result)
            ])
            f.write(content)
            f.write("\n")


if __name__ == "__main__":
    main()
