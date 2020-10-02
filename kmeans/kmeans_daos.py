"""Simple adaptation of kmeans to PyDAOS.

The kmeans.py (containing a kmeans done with the dataClay framework) is used
as the reference implementation. Naming and structures have been adapted to
make sense with PyDAOS.

For details and more documentation, check that reference implementation instead
of this.
"""

import os
import time
import uuid
import numpy as np
from sklearn.metrics import pairwise_distances

import pydaos


#############################################
# Constants / experiment values:
#############################################

POINTS_PER_FRAGMENT = int(os.environ["POINTS_PER_FRAGMENT"])
NUMBER_OF_FRAGMENTS = int(os.environ["NUMBER_OF_FRAGMENTS"])
DIMENSIONS = int(os.getenv("DIMENSIONS", "500"))
NUMBER_OF_CENTERS = int(os.getenv("NUMBER_OF_CENTERS", "20"))
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "10"))
NUMBER_OF_KMEANS_ITERATIONS = int(os.getenv("NUMBER_OF_KMEANS_ITERATIONS", "10"))

SEED = 42
MODE = 'uniform'

DAOS_POOL_UUID = os.environ["DAOS_POOL"]
DAOS_CONT_UUID = os.environ["DAOS_CONT"]

#############################################
#############################################

DAOS_CONT = pydaos.Cont(DAOS_POOL_UUID, DAOS_CONT_UUID)
DAOS_KV = DAOS_CONT.rootkv()

NP_FROMSTRING_DTYPE = np.dtype('float64')
NP_FROMSTRING_SHAPES = list()


def generate_points(num_points, dim, mode, seed):
    # Random generation distributions
    rand = {
        'normal': lambda k: np.random.normal(0, 1, k),
        'uniform': lambda k: np.random.random(k),
    }
    r = rand[mode]
    np.random.seed(seed)
    mat = np.array(
        [r(dim) for __ in range(num_points)]
    )
    # Normalize all points between 0 and 1
    mat -= np.min(mat)
    mx = np.max(mat)
    if mx > 0.0:
        mat /= mx

    return mat


def partial_sum(centers, frag_idx):
    partials = np.zeros((centers.shape[0], 2), dtype=object)

    arr = np.fromstring(
        DAOS_KV[str(frag_idx)], 
        dtype=NP_FROMSTRING_DTYPE
    ).reshape(
        NP_FROMSTRING_SHAPES[frag_idx]
    )

    close_centers = pairwise_distances(arr, centers).argmin(axis=1)
    for center_idx in range(len(centers)):
        indices = np.argwhere(close_centers == center_idx).flatten()
        partials[center_idx][0] = np.sum(arr[indices], axis=0)
        partials[center_idx][1] = indices.shape[0]
        
    return partials


def recompute_centers(partials):
    aggr = np.sum(partials, axis=0)

    centers = list()
    for sum_ in aggr:
        # centers with no elements are removed
        if sum_[1] != 0:
            centers.append(sum_[0] / sum_[1])
    return np.array(centers)


def kmeans_frag():
    centers = np.matrix(
        [np.random.random(DIMENSIONS) for _ in range(NUMBER_OF_CENTERS)]
    )

    for it in range(NUMBER_OF_KMEANS_ITERATIONS):
        print("Doing k-means iteration #%d/%d" % (it + 1, NUMBER_OF_KMEANS_ITERATIONS))

        partials = list()
        for i_frag in range(NUMBER_OF_FRAGMENTS):
            partial = partial_sum(centers, i_frag)
            partials.append(partial)

        centers = recompute_centers(partials)

    return centers


def main():

    print(f"""Starting experiment with the following:

POINTS_PER_FRAGMENT = {POINTS_PER_FRAGMENT}
NUMBER_OF_FRAGMENTS = {NUMBER_OF_FRAGMENTS}
DIMENSIONS = {DIMENSIONS}
NUMBER_OF_CENTERS = {NUMBER_OF_CENTERS}
NUMBER_OF_ITERATIONS = {NUMBER_OF_ITERATIONS}
NUMBER_OF_KMEANS_ITERATIONS = {NUMBER_OF_KMEANS_ITERATIONS}
""")

    start_time = time.time()

    for i in range(NUMBER_OF_FRAGMENTS):
        print("Generating fragment #%d" % (i + 1))

        fragment_data = generate_points(POINTS_PER_FRAGMENT, DIMENSIONS, MODE, SEED + i)
        DAOS_KV[str(i)] = fragment_data.tostring()
        NP_FROMSTRING_SHAPES.append(fragment_data.shape)
    
    # let gc deallocate that
    del fragment_data

    print("Generation/Load done")
    initialization_time = time.time()
    print("Starting kmeans")

    print("-----------------------------------------")
    print("-------------- RESULTS ------------------")
    print("-----------------------------------------")
    print("Initialization time: %f" % (initialization_time - start_time))

    result_times = list()

    # Run kmeans
    for i in range(NUMBER_OF_ITERATIONS):
        start_t = time.time()

        centers = kmeans_frag()

        end_t = time.time()

        kmeans_time = end_t - start_t
        print("k-means time (#%d/%d): %f" % (i + 1, NUMBER_OF_ITERATIONS, kmeans_time))

        result_times.append(kmeans_time)

    print("Ending kmeans")

    with open("results_daos.csv", "a") as f:
        for result in result_times:
            # Mangling everything with a ",".join
            content = ",".join([
                str(POINTS_PER_FRAGMENT),
                str(NUMBER_OF_FRAGMENTS),
                str(DIMENSIONS),
                str(NUMBER_OF_CENTERS),
                str(NUMBER_OF_KMEANS_ITERATIONS),
                "0",  # EXEC_IN_NVRAM makes no sense in DAOS
                "DAOS",
                str(result)
            ])
            f.write(content)
            f.write("\n")


if __name__ == "__main__":
    main()
