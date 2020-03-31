from __future__ import print_function

import time
import sys
import operator
import numpy as np

from dataclay import api

api.init()

from model.block import Block


#############################################
# Constants / experiment values:
#############################################

BLOCKSIZE = 4096
MATRIXSIZE = 7

GENERATE_BLOCKS = True
STORE_WITH_ALIAS = False

STRATEGY = "mm"

#############################################
#############################################

def matsum(matrix_a, matrix_b):
    """Multiply A * B, return resulting C."""

    n, m = len(matrix_a), len(matrix_b[0])

    matrix_c = list()
    for _i in range(n):
        row = list()
        matrix_c.append(row)
        for _j in range(m):
            block = Block()
            block.make_persistent()
            block.initialize_zeros(BLOCKSIZE, BLOCKSIZE)
            row.append(block)

    for i in range(n):
        for j in range(m):
            print("Evaluating output cell (%d, %d)" % (i, j))
            matrix_c[i][j].assign_sum(matrix_a[i][j], matrix_b[i][j])            
            #matrix_c[i][j].persist()

    return matrix_c


def prepare_block(name, coord_i, coord_j):
    """Create a persistent block or retrieve it."""
    alias = "%s%02d%02d" % (name, coord_i, coord_j)

    if GENERATE_BLOCKS:
        block = Block()

        print("About to prepare block %s" % alias)
        if not STORE_WITH_ALIAS:
            alias = None
        block.make_persistent(alias=alias)

        block.initialize_random(BLOCKSIZE, BLOCKSIZE)
    else:
        print("Retrieving block %s" % alias)
        block = Block.get_by_alias(alias)
    return block

def main():

    print("""Starting experiment with the following:

BLOCKSIZE = {blocksize}
MATRIXSIZE = {matrixsize}
STRATEGY = {strategy}
""".format(blocksize=BLOCKSIZE,
           matrixsize=MATRIXSIZE,
           strategy=STRATEGY)
    )

    start_time = time.time()

    print("Preparing B")
    matrix_b = [[prepare_block("B", i, j) for i in range(MATRIXSIZE)] for j in range(MATRIXSIZE)]
    print("Preparing A")
    matrix_a = [[prepare_block("A", i, j) for i in range(MATRIXSIZE)] for j in range(MATRIXSIZE)]
 
    print("Generation/Load done")
    initialization_time = time.time()
    print("Starting matsum")

    # Run matsum
    matrix_c = matsum(matrix_a, matrix_b)

    print("Ending matsum")

    matsum_time = time.time()

    print("Second round of matsum")
    matrix_c = matsum(matrix_a, matrix_b)

    print("Ending matsum")
    matsum_2nd = time.time()

    print("-----------------------------------------")
    print("-------------- RESULTS ------------------")
    print("-----------------------------------------")
    print("Initialization time: %f" % (initialization_time - start_time))
    print("Matsum time: %f" % (matsum_time - initialization_time))
    print("Matsum 2nd round time: %f" % (matsum_2nd - matsum_time))
    print("Total time: %f" % (matsum_2nd - start_time))
    print("-----------------------------------------")


if __name__ == "__main__":
    main()
    api.finish()
