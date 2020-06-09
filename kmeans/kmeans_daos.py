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
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import pydaos


#############################################
# Constants / experiment values:
#############################################

NUMPOINTS = 2000000
FRAGMENTS = 100
DIMENSIONS = 5000
CENTERS = 20
MODE = 'uniform'
SEED = 42
ITERATIONS = 5
PARALLELLISM = 4

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


def cluster_and_partial_sums(centres, norm, fragment_idx):
    mat = np.fromstring(
        DAOS_KV[str(fragment_idx)], 
        dtype=NP_FROMSTRING_DTYPE
    ).reshape(
        NP_FROMSTRING_SHAPES[fragment_idx]
    )

    ret = np.array(np.zeros(centres.shape))
    n = mat.shape[0]
    c = centres.shape[0]
    labels = np.zeros(n, dtype=int)
    # labels are ignored atm

    # Compute the big stuff
    associates = np.zeros(c, dtype=int)
    # Get the labels for each point
    for (i, point) in enumerate(mat):
        distances = np.zeros(c)
        for (j, centre) in enumerate(centres):
            distances[j] = np.linalg.norm(point - centre, norm)
        labels[i] = np.argmin(distances)
        associates[labels[i]] += 1

    # Add each point to its associate centre
    for (i, point) in enumerate(mat):
        ret[labels[i]] += point / associates[labels[i]]
    return ret



def kmeans_frag(dimensions, num_centres=10, iterations=20, seed=0., epsilon=1e-9, norm='l2'):
    """
    A fragment-based K-Means algorithm.
    Given a set of fragments (which can be either PSCOs or future objects that
    point to PSCOs), the desired number of clusters and the maximum number of
    iterations, compute the optimal centres and the index of the centre
    for each point.
    PSCO.mat must be a NxD float np.matrix, where D = dimensions
    :param dimensions: Number of dimensions
    :param num_centres: Number of centers
    :param iterations: Maximum number of iterations
    :param seed: Random seed
    :param epsilon: Epsilon (convergence distance)
    :param norm: Norm
    :return: Final centers and labels
    """
    # Choose the norm among the available ones
    norms = {
        'l1': 1,
        'l2': 2,
    }
    # Set the random seed
    np.random.seed(seed)
    # Centres is usually a very small matrix, so it is affordable to have it in
    # the master.
    centres = np.matrix(
        [np.random.random(dimensions) for _ in range(num_centres)]
    )

    cluster_and_partial_sums_partial = partial(cluster_and_partial_sums, centres, norms[norm])
    with ThreadPoolExecutor(max_workers=PARALLELLISM) as executor:
        for it in range(iterations):
            print("Doing iteration #%d/%d" % (it + 1, iterations))
            partial_results = executor.map(cluster_and_partial_sums_partial, range(FRAGMENTS))

            # Bring the partial sums to the master, compute new centres when syncing
            new_centres = np.matrix(np.zeros(centres.shape))
            for partial_res in partial_results:
                # Mean of means, single step
                new_centres += partial_res / float(FRAGMENTS)

            if np.linalg.norm(centres - new_centres, norms[norm]) < epsilon:
                # Convergence criterion is met
                break
            # Convergence criterion is not met, update centres
            centres = new_centres

    # Some technical debt on COMPSs code here, leaving None. Computationally equivalent
    return centres, None


def main():

    print("""Starting experiment with the following:

NUMPOINTS = {numpoints}
FRAGMENTS = {fragments}
DIMENSIONS = {dimensions}
CENTERS = {centers}
MODE = '{mode}'
SEED = {seed}
ITERATIONS = {iterations}
PARALLELLISM = {parallellism}
""".format(numpoints=NUMPOINTS,
           fragments=FRAGMENTS,
           dimensions=DIMENSIONS,
           centers=CENTERS,
           mode=MODE,
           seed=SEED,
           iterations=ITERATIONS,
           parallellism=PARALLELLISM)
    )
    start_time = time.time()

    # Generate the data
    points_per_fragment = NUMPOINTS // FRAGMENTS

    for i, l in enumerate(range(0, NUMPOINTS, points_per_fragment)):

        print("Generating fragment #%d" % (i + 1))

        # Note that the seed is different for each fragment.
        # This is done to avoid having repeated data.
        r = min(NUMPOINTS, l + points_per_fragment)

        fragment_data = generate_points(r - l, DIMENSIONS, MODE, SEED + l)
        DAOS_KV[str(i)] = fragment_data.tostring()
        NP_FROMSTRING_SHAPES.append(fragment_data.shape)
    
    # let gc deallocate that
    del fragment_data

    print("Generation/Load done")
    initialization_time = time.time()
    print("Starting kmeans")

    # Run kmeans
    num_centers = CENTERS
    centres, labels = kmeans_frag(dimensions=DIMENSIONS,
                                  num_centres=num_centers,
                                  iterations=ITERATIONS,
                                  seed=SEED)
    print("Ending kmeans")

    kmeans_time = time.time()

    print("-----------------------------------------")
    print("-------------- RESULTS ------------------")
    print("-----------------------------------------")
    print("Initialization time: %f" % (initialization_time - start_time))
    print("Kmeans time: %f" % (kmeans_time - initialization_time))
    print("-----------------------------------------")


if __name__ == "__main__":
    main()
