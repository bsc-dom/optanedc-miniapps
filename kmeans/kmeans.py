import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from operator import methodcaller

from dataclay import api

api.init()

from model.fragment import Fragment


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

GENERATE_FRAGMENTS = True
STORE_WITH_ALIAS = False

#############################################
#############################################


def kmeans_frag(fragments, dimensions, num_centres=10, iterations=20, seed=0., epsilon=1e-9, norm='l2'):
    """
    A fragment-based K-Means algorithm.
    Given a set of fragments (which can be either PSCOs or future objects that
    point to PSCOs), the desired number of clusters and the maximum number of
    iterations, compute the optimal centres and the index of the centre
    for each point.
    PSCO.mat must be a NxD float np.matrix, where D = dimensions
    :param fragments: Number of fragments
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

    with ThreadPoolExecutor(max_workers=PARALLELLISM) as executor:
        for it in range(iterations):
            print("Doing iteration #%d/%d" % (it + 1, iterations))
            partial_results = executor.map(methodcaller('cluster_and_partial_sums', centres, norms[norm]), fragments)

            # Bring the partial sums to the master, compute new centres when syncing
            new_centres = np.matrix(np.zeros(centres.shape))
            for partial in partial_results:
                # Mean of means, single step
                new_centres += partial / float(len(fragments))

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
    fragment_list = []
    # Prevent infinite loops in case of not-so-smart users
    points_per_fragment = NUMPOINTS // FRAGMENTS

    for i, l in enumerate(range(0, NUMPOINTS, points_per_fragment)):
        alias = "fragment%03d" % i

        if GENERATE_FRAGMENTS:
            print("Generating fragment #%d" % (i + 1))
            if not STORE_WITH_ALIAS:
                alias = None

            # Note that the seed is different for each fragment.
            # This is done to avoid having repeated data.
            r = min(NUMPOINTS, l + points_per_fragment)

            fragment = Fragment()
            fragment.make_persistent(alias=alias)
            fragment.generate_points(r - l, DIMENSIONS, MODE, SEED + l)
        else:
            fragment = Fragment.get_by_alias(alias)

        fragment_list.append(fragment)

    print("Generation/Load done")
    initialization_time = time.time()
    print("Starting kmeans")

    # Run kmeans
    num_centers = CENTERS
    centres, labels = kmeans_frag(fragments=fragment_list,
                                  dimensions=DIMENSIONS,
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
    api.finish()
