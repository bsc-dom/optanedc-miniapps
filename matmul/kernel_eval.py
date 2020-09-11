"""Evaluate the kernel itself.

This code is designed with the idea of evaluating the computation required by
the kernel.

The different kernels can be timed and that would give the computation
performance that can be achieved (as an upper bound).
"""

import os
import time
import numpy as np

from npp2nvm import np_persist

BLOCKSIZE = int(os.environ["BLOCKSIZE"])
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "5"))

# Certain combinations of those flags make no sense or are ill-defined
# for instance: EXEC_IN_NVRAM without the other two, which makes no sense.
INPUT_IN_NVRAM = bool(int(os.getenv("INPUT_IN_NVRAM", "0")))
# also, EXEC_IN_NVRAM implies RESULT_IN_NVRAM
EXEC_IN_NVRAM = bool(int(os.getenv("EXEC_IN_NVRAM", "0")))
RESULT_IN_NVRAM = bool(int(os.getenv("RESULT_IN_NVRAM", "0")))

# Define this only to evaluate a full row x column operation
# --which is more than the "kernel" ~= FMA operation.
MATRIX_SIDE_SIZE = int(os.getenv("MATRIX_SIDE_SIZE", "0"))

def fma(a: np.ndarray, b: np.ndarray, c: np.ndarray):
    c += a @ b

def generate_data(input_size, output_size):
    a_blocks = list()
    b_blocks = list()
    c_blocks = list()
    
    for _ in range(input_size):
        a = np.random.random([BLOCKSIZE, BLOCKSIZE])
        b = np.random.random([BLOCKSIZE, BLOCKSIZE])
        # Only for evaluating in-place excution on Optane DC
        if INPUT_IN_NVRAM:
            a = np_persist(a)
            b = np_persist(b)
        a_blocks.append(a)
        b_blocks.append(b)

    for _ in range(output_size):
        c = np.zeros([BLOCKSIZE, BLOCKSIZE])
        if EXEC_IN_NVRAM:
            c = np_persist(c)
        c_blocks.append(c)

    return a_blocks, b_blocks, c_blocks


if __name__ == "__main__":
    print(f"""***
BLOCKSIZE: {BLOCKSIZE}
NUMBER_OF_ITERATIONS: {NUMBER_OF_ITERATIONS}
INPUT_IN_NVRAM: {INPUT_IN_NVRAM}
EXEC_IN_NVRAM: {EXEC_IN_NVRAM}
RESULT_IN_NVRAM: {RESULT_IN_NVRAM}
MATRIX_SIDE_SIZE: {MATRIX_SIDE_SIZE}
***""")
    start_time = time.time()

    if MATRIX_SIDE_SIZE < 2:
        a_blocks, b_blocks, c_blocks = generate_data(NUMBER_OF_ITERATIONS, NUMBER_OF_ITERATIONS)
        print("Generation time: %f" % (time.time() - start_time))

        kernel_time = list()
        for a, b, c in zip(a_blocks, b_blocks, c_blocks):
            start_time = time.time()
            fma(a, b, c)
            kernel_time.append(time.time() - start_time)

        print("Execution times for the kernel: %r" % kernel_time)
    else:
        a_blocks, b_blocks, c_blocks = list(), list(), list()
        for _ in range(NUMBER_OF_ITERATIONS):
            a, b, c = generate_data(MATRIX_SIDE_SIZE, 1)
            a_blocks.append(a)
            b_blocks.append(b)
            c_blocks.append(c[0])

        print("Generation time: %f" % (time.time() - start_time))

        rowcolmul_time = list()

        for row, column, result in zip(a_blocks, b_blocks, c_blocks):
            start_time = time.time()
            for a, b in zip(row, column):
                fma(a, b, c)
            if RESULT_IN_NVRAM and not EXEC_IN_NVRAM:
                c = np_persist(c)

            rowcolmul_time.append(time.time() - start_time)

        print("Execution times for the row x column multiplication: %r" % rowcolmul_time)
