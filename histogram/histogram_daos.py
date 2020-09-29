"""Simple adaptation of histogram to PyDAOS.

The histogram.py (containing a histogram done with the dataClay framework) is
used as the reference implementation. Naming and structures have been adapted
to make sense with PyDAOS.

For details and more documentation, check that reference implementation instead
of this.
"""

import time
import os

import numpy as np
import pydaos


#############################################
# Constants / experiment values:
#############################################

NUMVALUES = 8000 * 1000 * 1000
FRAGMENTS = 100
SEED = 420

DAOS_POOL_UUID = os.environ["DAOS_POOL"]
DAOS_CONT_UUID = os.environ["DAOS_CONT"]

#############################################
#############################################

DAOS_CONT = pydaos.Cont(DAOS_POOL_UUID, DAOS_CONT_UUID)
DAOS_KV = DAOS_CONT.rootkv()

NP_FROMSTRING_DTYPE = np.dtype('float64')
NP_FROMSTRING_SHAPES = list()


def generation():
    experiment = list()
    points_per_frag = NUMVALUES // FRAGMENTS
    seed = SEED

    for i in range(FRAGMENTS):
        print("Proceeding to generate fragment #%d" % (i + 1))

        # Random generation distributions
        np.random.seed(seed)
        values = np.random.f(10, 2, points_per_frag)

        DAOS_KV[str(i)] = values.tostring()
        NP_FROMSTRING_SHAPES.append(values.shape)

        seed += 1


def histogram():
    bins = np.concatenate((np.arange(0,10, 0.1), np.arange(10, 50), [np.infty]))

    partial_results = list()

    for frag_idx in range(FRAGMENTS):
        values = np.fromstring(
            DAOS_KV[str(frag_idx)], 
            dtype=NP_FROMSTRING_DTYPE
        ).reshape(
            NP_FROMSTRING_SHAPES[frag_idx]
        )

        part_res, _ = np.histogram(values, bins)
        partial_results.append(part_res)

    return np.sum(partial_results, axis=0)
    

def main():

    print("""Starting experiment with the following:

NUMVALUES = {numvalues}
FRAGMENTS = {fragments}
SEED = {seed}
""".format(numvalues=NUMVALUES,
           fragments=FRAGMENTS,
           seed=SEED)
    )
    start_time = time.time()

    # Generation of data
    experiment = generation()

    print("Generation/Load done")
    initialization_time = time.time()
    print("Starting histogram")

    # Run histogram
    result = histogram()
    print("Ending histogram (1st)")

    histogram_time = time.time()

    # Run histogram again
    result = histogram()
    print("Ending histogram (2nd)")

    histogram_time_bis = time.time()

    print("-----------------------------------------")
    print("-------------- RESULTS ------------------")
    print("-----------------------------------------")
    print("Initialization time: %f" % (initialization_time - start_time))
    print("Histogram time (1st run): %f" % (histogram_time - initialization_time))
    print("Histogram time (2nd run): %f" % (histogram_time_bis - histogram_time))
    print("-----------------------------------------")


if __name__ == "__main__":
    main()
