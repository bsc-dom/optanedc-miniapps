"""Evaluate the kernel iself.

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

EXEC_IN_NVRAM = bool(int(os.getenv("EXEC_IN_NVRAM", "0")))

def block_sum(a: np.ndarray, b: np.ndarray):
    ret = a + b
    return ret

def generate_data():
    a_blocks = list()
    b_blocks = list()

    for _ in range(NUMBER_OF_ITERATIONS):
        a = np.random.random([BLOCKSIZE, BLOCKSIZE])
        b = np.random.random([BLOCKSIZE, BLOCKSIZE])

        # Only for evaluating in-place excution on Optane DC
        if EXEC_IN_NVRAM:
            a = np_persist(a)
            b = np_persist(b)

        a_blocks.append(a)
        b_blocks.append(b)

    return a_blocks, b_blocks


if __name__ == "__main__":
    print(f"""***
BLOCKSIZE: {BLOCKSIZE}
NUMBER_OF_ITERATIONS: {NUMBER_OF_ITERATIONS}
EXEC_IN_NVRAM: {EXEC_IN_NVRAM}
***""")
    start_time = time.time()
    a_blocks, b_blocks = generate_data()
    print("Generation time: %f" % (time.time() - start_time))

    kernel_time = list()
    for a, b in zip(a_blocks, b_blocks):
        start_time = time.time()
        block_sum(a, b)
        kernel_time.append(time.time() - start_time)

    print("Execution times for the kernel: %r" % kernel_time)
