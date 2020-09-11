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
DIMENSIONS = int(os.getenv("DIMENSIONS", "5000"))
NUMBER_OF_CENTERS = int(os.getenv("NUMBER_OF_CENTERS", "20"))
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "5"))
EXEC_IN_NVRAM = bool(int(os.getenv("EXEC_IN_NVRAM", "0")))

def cluster_and_partial_sums(mat: np.ndarray, centres: np.ndarray):
    ret = np.array(np.zeros(centres.shape))
    n = mat.shape[0]
    c = centres.shape[0]
    labels = np.zeros(n, dtype=int)

    # Compute the big stuff
    associates = np.zeros(c, dtype=int)
    # Get the labels for each point
    for (i, point) in enumerate(mat):
        distances = np.zeros(c)
        for (j, centre) in enumerate(centres):
            distances[j] = np.linalg.norm(point - centre, 2)
        labels[i] = np.argmin(distances)
        associates[labels[i]] += 1

    # Add each point to its associate centre
    for (i, point) in enumerate(mat):
        ret[labels[i]] += point / associates[labels[i]]
    return ret

def generate_data():
    blocks = list()

    for _ in range(NUMBER_OF_ITERATIONS):
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
EXEC_IN_NVRAM: {EXEC_IN_NVRAM}
***""")

    start_time = time.time()
    blocks = generate_data()
    print("Generation time: %f" % (time.time() - start_time))

    kernel_time = list()
    for block in blocks:
        centers = np.matrix(
            [np.random.random(DIMENSIONS) for _ in range(NUMBER_OF_CENTERS)]
        )
        start_time = time.time()
        cluster_and_partial_sums(block, centers)
        kernel_time.append(time.time() - start_time)

    print("Execution times for the kernel: %r" % kernel_time)
