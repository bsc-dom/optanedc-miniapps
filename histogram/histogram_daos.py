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

POINTS_PER_FRAGMENT = int(os.environ["POINTS_PER_FRAGMENT"])
NUMBER_OF_FRAGMENTS = int(os.environ["NUMBER_OF_FRAGMENTS"])
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "10"))

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

    seed = SEED

    for i in range(NUMBER_OF_FRAGMENTS):
        print("Proceeding to generate fragment #%d" % (i + 1))

        # Random generation distributions
        np.random.seed(seed)
        values = np.random.f(10, 2, POINTS_PER_FRAGMENT)

        DAOS_KV[str(i)] = values.tostring()
        NP_FROMSTRING_SHAPES.append(values.shape)

        seed += 1


def histogram():
    bins = np.concatenate((np.arange(0,10, 0.1), np.arange(10, 50), [np.infty]))

    partial_results = list()

    for frag_idx in range(NUMBER_OF_FRAGMENTS):
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

    print(f"""Starting experiment with the following:

POINTS_PER_FRAGMENT = {POINTS_PER_FRAGMENT}
NUMBER_OF_FRAGMENTS = {NUMBER_OF_FRAGMENTS}
NUMBER_OF_ITERATIONS = {NUMBER_OF_ITERATIONS}

SEED = {SEED}
""")
    start_time = time.time()

    # Generation of data
    generation()

    print("Generation/Load done")
    initialization_time = time.time()
    print("Starting histogram")

    print("-----------------------------------------")
    print("-------------- RESULTS ------------------")
    print("-----------------------------------------")
    print("Initialization time: %f" % (initialization_time - start_time))

    result_times = list()

    # Run histogram
    for i in range(NUMBER_OF_ITERATIONS):
        start_t = time.time()
        result = histogram()
        end_t = time.time()

        histogram_time = end_t - start_t
        print("Histogram time (#%d/%d): %f" % (i + 1, NUMBER_OF_ITERATIONS, histogram_time))

        result_times.append(histogram_time)

    print("Ending histogram")
    print("-----------------------------------------")

    with open("results_daos.csv", "a") as f:
        for result in result_times:
            # Mangling everything with a ",".join
            content = ",".join([
                str(POINTS_PER_FRAGMENT),
                str(NUMBER_OF_FRAGMENTS),
                "0",  # EXEC_IN_NVRAM makes no sense in DAOS
                "DAOS",
                str(result)
            ])
            f.write(content)
            f.write("\n")


if __name__ == "__main__":
    main()
