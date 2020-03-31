import time
import numpy as np

from dataclay import api

api.init()

from model.fragment import Fragment


#############################################
# Constants / experiment values:
#############################################

NUMVALUES = 8000 * 1000 * 1000
FRAGMENTS = 100
SEED = 420

#############################################
#############################################


def generation():
    experiment = list()
    points_per_frag = NUMVALUES // FRAGMENTS
    seed = SEED

    for i in range(FRAGMENTS):
        print("Proceeding to generate fragment #%d" % (i + 1))
        frag = Fragment()
        frag.make_persistent()
        frag.generate_values(points_per_frag, seed)
        experiment.append(frag)

        seed += 1

    return experiment


def histogram(experiment):
    bins = np.concatenate((np.arange(0,10, 0.1), np.arange(10, 50), [np.infty]))

    partial_results = list()

    for frag in experiment:
        partial_results.append(frag.partial_histogram(bins))

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
    result = histogram(experiment)
    print("Ending histogram (1st)")

    histogram_time = time.time()

    # Run histogram again
    result = histogram(experiment)
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
    api.finish()
