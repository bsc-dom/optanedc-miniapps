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
from sklearn.metrics import pairwise_distances

POINTS_PER_FRAGMENT = int(os.environ["POINTS_PER_FRAGMENT"])
DIMENSIONS = int(os.getenv("DIMENSIONS", "500"))
NUMBER_OF_CENTERS = int(os.getenv("NUMBER_OF_CENTERS", "20"))
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "10"))
NUMBER_OF_GENERATIONS = int(os.getenv("NUMBER_OF_GENERATIONS", "-1"))
EXEC_IN_NVRAM = bool(int(os.getenv("EXEC_IN_NVRAM", "0")))


def partial_sum(arr: np.ndarray, centres: np.ndarray):
    partials = np.zeros((centres.shape[0], 2), dtype=object)
    close_centres = pairwise_distances(arr, centres).argmin(axis=1)
    for center_idx in range(len(centres)):
        indices = np.argwhere(close_centres == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]
    
    return partials

def generate_data():
    blocks = list()

    n = NUMBER_OF_GENERATIONS if NUMBER_OF_GENERATIONS > 0 else NUMBER_OF_ITERATIONS

    for _ in range(n):
        mat = np.array(
            [np.random.random(DIMENSIONS) for __ in range(POINTS_PER_FRAGMENT)]
        )
        # Normalize all points between 0 and 1
        mat -= np.min(mat)
        mx = np.max(mat)
        if mx > 0.0:
            mat /= mx

        # Only for evaluating in-place excution on Optane DC
        if EXEC_IN_NVRAM:
            mat = np_persist(mat)

        blocks.append(mat)

    return blocks


if __name__ == "__main__":
    print(f"""***
POINTS_PER_FRAGMENT: {POINTS_PER_FRAGMENT}
DIMENSIONS: {DIMENSIONS}
NUMBER_OF_CENTERS: {NUMBER_OF_CENTERS}
NUMBER_OF_ITERATIONS: {NUMBER_OF_ITERATIONS}
NUMBER_OF_GENERATIONS: {NUMBER_OF_GENERATIONS}
EXEC_IN_NVRAM: {EXEC_IN_NVRAM}
***""")

    start_time = time.time()
    blocks = generate_data()
    print("Generation time: %f" % (time.time() - start_time))

    kernel_time = list()
    for _, block in zip(range(NUMBER_OF_ITERATIONS), cycle(blocks)):
        centers = np.matrix(
            [np.random.random(DIMENSIONS) for _ in range(NUMBER_OF_CENTERS)]
        )
        start_time = time.time()
        partial_sum(block, centers)
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
                str(POINTS_PER_FRAGMENT),
                str(DIMENSIONS),
                str(NUMBER_OF_CENTERS),
                str(int(EXEC_IN_NVRAM)),
                mode,
                str(result)
            ])
            f.write(content)
            f.write("\n")
