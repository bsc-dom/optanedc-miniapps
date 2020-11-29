from __future__ import print_function

import time
import sys
import numpy as np
import os

from dataclay import api

api.init()

from model.block import Block


#############################################
# Constants / experiment values:
#############################################

BLOCKSIZE = int(os.environ["BLOCKSIZE"])
MATRIXSIZE = int(os.environ["MATRIXSIZE"])

NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "10"))
INPUT_IN_NVRAM = bool(int(os.getenv("INPUT_IN_NVRAM", "0")))
RESULT_IN_NVRAM = bool(int(os.getenv("RESULT_IN_NVRAM", "0")))

#############################################
#############################################

def matsum(matrix_a, matrix_b, matrix_c):
    """Add A * B, assign result to C."""

    n, m = len(matrix_a), len(matrix_b[0])

    for i in range(n):
        for j in range(m):
            matrix_c[i][j].assign_sum(matrix_a[i][j], matrix_b[i][j])

            if RESULT_IN_NVRAM:
                matrix_c[i][j].persist_to_nvram()


def prepare_matrices():
    matrix_a = list()
    matrix_b = list()
    matrix_c = list()

    for i in range(MATRIXSIZE):
        a_row = list()
        b_row = list()
        c_row = list()

        matrix_a.append(a_row)
        matrix_b.append(b_row)
        matrix_c.append(c_row)

        for j in range(MATRIXSIZE):
            a_block = Block()
            b_block = Block()
            c_block = Block()

            a_row.append(a_block)
            b_row.append(b_block)
            c_row.append(c_block)

            a_block.make_persistent()
            b_block.make_persistent()
            c_block.make_persistent()

            a_block.initialize_random(BLOCKSIZE, BLOCKSIZE)
            b_block.initialize_random(BLOCKSIZE, BLOCKSIZE)
            # c_block is not initialized, as the numpy matrix addition creates the structure

            if INPUT_IN_NVRAM:
                a_block.persist_to_nvram()
                b_block.persist_to_nvram()

    return matrix_a, matrix_b, matrix_c


def main():

    print(f"""Starting experiment with the following:

BLOCKSIZE = {BLOCKSIZE}
MATRIXSIZE = {MATRIXSIZE}
NUMBER_OF_ITERATIONS = {NUMBER_OF_ITERATIONS}
INPUT_IN_NVRAM = {INPUT_IN_NVRAM}
RESULT_IN_NVRAM = {RESULT_IN_NVRAM}
""")

    start_time = time.time()

    print("Preparing matrices")
    matrix_a, matrix_b, matrix_c = prepare_matrices()

    initialization_time = time.time()

    print("-----------------------------------------")
    print("-------------- RESULTS ------------------")
    print("-----------------------------------------")
    print("Initialization time: %f" % (initialization_time - start_time))
    print("Starting matsum")

    result_times = list()

    ##########################################################################
    # Matsum is a fast application for which the first execution may have a
    # bogus execution time (distorted timing).
    # Workaround for warming up everything nicely is to simply perform a 
    # "fake" matmul, which will be the slowest one, and ignore it.
    time.sleep(5)
    matsum(matrix_a, matrix_b, matrix_c)
    # Cleanup matrix_c
    for row in matrix_c:
        for block in row:
            block.block = None
    ##########################################################################

    # Run matsum
    for i in range(NUMBER_OF_ITERATIONS):
        start_t = time.time()
        
        matsum(matrix_a, matrix_b, matrix_c)

        end_t = time.time()

        matsum_time = end_t - start_t

        print("matsum time (#%d/%d): %f" % (i + 1, NUMBER_OF_ITERATIONS, matsum_time))

        result_times.append(matsum_time)

        # Cleanup matrix_c
        for row in matrix_c:
            for block in row:
                block.block = None

    print("Ending matsum")
    print("-----------------------------------------")

    # Are we in Memory Mode?
    # Easy to know: check if there is more than 1TiB of memory
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    mem_tib = mem_bytes / (1024**4)
    mode = "MM" if mem_tib > 1 else "AD"

    with open("results_app.csv", "a") as f:
        for result in result_times:
            # Mangling everything with a ",".join
            content = ",".join([
                str(BLOCKSIZE),
                str(MATRIXSIZE),
                str(int(INPUT_IN_NVRAM)),
                str(int(RESULT_IN_NVRAM)),
                mode,
                str(result)
            ])
            f.write(content)
            f.write("\n")


if __name__ == "__main__":
    main()
    api.finish()
