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

POINTS_PER_FRAGMENT = int(os.environ["POINTS_PER_FRAGMENT"])
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "10"))
NUMBER_OF_GENERATIONS = int(os.getenv("NUMBER_OF_GENERATIONS", "-1"))
EXEC_IN_NVRAM = bool(int(os.getenv("EXEC_IN_NVRAM", "0")))

def partial_histogram(values: np.ndarray, bins: np.ndarray):
    values, _ = np.histogram(values, bins)
    return values

def generate_data():
    blocks = list()
    n = NUMBER_OF_GENERATIONS if NUMBER_OF_GENERATIONS > 0 else NUMBER_OF_ITERATIONS
    for _ in range(n):
        values = np.random.f(10, 2, POINTS_PER_FRAGMENT)

        # Only for evaluating in-place excution on Optane DC
        if EXEC_IN_NVRAM:
            values = np_persist(values)

        blocks.append(values)

    bins = np.concatenate((np.arange(0,10, 0.1), np.arange(10, 50), [np.infty]))

    return bins, blocks


if __name__ == "__main__":
    print(f"""***
POINTS_PER_FRAGMENT: {POINTS_PER_FRAGMENT}
NUMBER_OF_ITERATIONS: {NUMBER_OF_ITERATIONS}
NUMBER_OF_GENERATIONS: {NUMBER_OF_GENERATIONS}
EXEC_IN_NVRAM: {EXEC_IN_NVRAM}
***""")

    start_time = time.time()
    bins, blocks = generate_data()
    print("Generation time: %f" % (time.time() - start_time))

    kernel_time = list()
    for _, block in zip(range(NUMBER_OF_ITERATIONS), cycle(blocks)):
        start_time = time.time()
        partial_histogram(block, bins)
        kernel_time.append(time.time() - start_time)

    print("Execution times for the kernel: %r" % kernel_time)

    with open("results_kernel.csv", "a") as f:
        for result in evaluation_time[-10:]:
            # I can't be bothered to use a proper CSV writer, I'm gonna just mangle everything here
            content = ",".join([
                str(POINTS_PER_FRAGMENT),
                str(int(EXEC_IN_NVRAM)),
                "0", # NUMA BINDING, reseracher should explicitly set if appropriate
                "?", # MODE, researcher MUST set it
                str(result)
            ])
            f.write(content)
            f.write("\n")
