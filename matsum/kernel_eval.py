"""Evaluate the kernel iself.

This code is designed with the idea of evaluating the computation required by
the kernel.

The different kernels can be timed and that would give the computation
performance that can be achieved (as an upper bound).
"""

import os
import time
import numpy as np
from itertools import cycle

from npp2nvm import np_persist

BLOCKSIZE = int(os.environ["BLOCKSIZE"])
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "10"))
NUMBER_OF_GENERATIONS = int(os.getenv("NUMBER_OF_GENERATIONS", "-1"))
EXEC_IN_NVRAM = bool(int(os.getenv("EXEC_IN_NVRAM", "0")))

def block_sum(a: np.ndarray, b: np.ndarray):
    ret = a + b
    return ret

def generate_data():
    a_blocks = list()
    b_blocks = list()
    n = NUMBER_OF_GENERATIONS if NUMBER_OF_GENERATIONS > 0 else NUMBER_OF_ITERATIONS
    for _ in range(n):
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
NUMBER_OF_GENERATIONS: {NUMBER_OF_GENERATIONS}
EXEC_IN_NVRAM: {EXEC_IN_NVRAM}
***""")
    start_time = time.time()
    a_blocks, b_blocks = generate_data()
    print("Generation time: %f" % (time.time() - start_time))

    kernel_time = list()
    for _, a, b in zip(range(NUMBER_OF_ITERATIONS), cycle(a_blocks), cycle(b_blocks)):
        start_time = time.time()
        block_sum(a, b)
        kernel_time.append(time.time() - start_time)

    print("Execution times for the kernel: %r" % kernel_time)

    with open("results_kernel.csv", "a") as f:
        for result in evaluation_time[-10:]:
            # I can't be bothered to use a proper CSV writer, I'm gonna just mangle everything here
            content = ",".join([
                str(BLOCKSIZE),
                str(int(EXEC_IN_NVRAM)),
                "0", # NUMA BINDING, reseracher should explicitly set if appropriate
                "?", # MODE, researcher MUST set it
                str(result)
            ])
            f.write(content)
            f.write("\n")
