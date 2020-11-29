"""Evaluate the kernel itself.

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
INPUT_IN_NVRAM = bool(int(os.getenv("INPUT_IN_NVRAM", "0")))
RESULT_IN_NVRAM = bool(int(os.getenv("RESULT_IN_NVRAM", "0")))

def block_sum(a: np.ndarray, b: np.ndarray):
    ret = a + b
    if RESULT_IN_NVRAM:
        ret = np_persist(ret)
    return ret

def generate_data():
    a_blocks = list()
    b_blocks = list()
    n = NUMBER_OF_GENERATIONS if NUMBER_OF_GENERATIONS > 0 else NUMBER_OF_ITERATIONS
    for _ in range(n):
        a = np.random.random([BLOCKSIZE, BLOCKSIZE])
        b = np.random.random([BLOCKSIZE, BLOCKSIZE])

        # Only for evaluating in-place excution on Optane DC
        if INPUT_IN_NVRAM:
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
INPUT_IN_NVRAM: {INPUT_IN_NVRAM}
RESULT_IN_NVRAM: {RESULT_IN_NVRAM}
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

    # Are we in Memory Mode?
    # Easy to know: check if there is more than 1TiB of memory
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    mem_tib = mem_bytes / (1024**4)
    mode = "MM" if mem_tib > 1 else "AD"

    with open("results_kernel.csv", "a") as f:
        for result in kernel_time[-10:]:
            # Mangling everything with a ",".join
            content = ",".join([
                str(BLOCKSIZE),
                str(int(INPUT_IN_NVRAM)),
                str(int(RESULT_IN_NVRAM)),
                mode,
                str(result)
            ])
            f.write(content)
            f.write("\n")
