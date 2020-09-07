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

POINTS_PER_FRAGMENT = int(os.environ["POINTS_PER_FRAGMENT"])
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "5"))
EXEC_IN_NVRAM = bool(int(os.getenv("EXEC_IN_NVRAM", "0")))

def partial_histogram(values: np.ndarray, bins: np.ndarray):
    values, _ = np.histogram(values, bins)
    return values

def generate_data():
    blocks = list()
    for _ in range(NUMBER_OF_ITERATIONS):
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
EXEC_IN_NVRAM: {EXEC_IN_NVRAM}
***""")

    start_time = time.time()
    bins, blocks = generate_data()
    print("Generation time: %f" % (time.time() - start_time))

    kernel_time = list()
    for block in blocks:
        start_time = time.time()
        partial_histogram(block, bins)
        kernel_time.append(time.time() - start_time)

    print("Execution times for the kernel: %r" % kernel_time)
