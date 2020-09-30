import time
import os

from dataclay import api

api.init()

from model.fragment import Fragment

import numpy as np


#############################################
# Constants / experiment values:
#############################################

POINTS_PER_FRAGMENT = int(os.environ["POINTS_PER_FRAGMENT"])
NUMBER_OF_FRAGMENTS = int(os.environ["NUMBER_OF_FRAGMENTS"])
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "10"))

SEED = 420

#############################################
#############################################


def generation():
    experiment = list()
    seed = SEED

    for i in range(NUMBER_OF_FRAGMENTS):
        print("Proceeding to generate fragment #%d" % (i + 1))
        frag = Fragment()
        frag.make_persistent()
        frag.generate_values(POINTS_PER_FRAGMENT, seed)
        frag.persist_to_nvram()
        
        experiment.append(frag)

        seed += 1

    return experiment


def histogram(experiment):
    bins = np.concatenate((np.arange(0,10, 0.1), np.arange(10, 50), [np.infty]))

    partial_results = list()

    for frag in experiment:
        # The frag.values getter will retrieve the object
        part_res, _ = np.histogram(frag.values, bins)
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
    experiment = generation()

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
        result = histogram(experiment)
        end_t = time.time()

        histogram_time = end_t - start_t
        print("Histogram time (#%d/%d): %f" % (i + 1, NUMBER_OF_ITERATIONS, histogram_time))

        result_times.append(histogram_time)

    print("-----------------------------------------")

    with open("results_dcnonactive.csv", "a") as f:
        for result in result_times:
            # Mangling everything with a ",".join
            content = ",".join([
                str(POINTS_PER_FRAGMENT),
                str(NUMBER_OF_FRAGMENTS),
                "0",  # EXEC_IN_NVRAM makes no sense under non-active configuration
                "DC-NONACT",
                str(result)
            ])
            f.write(content)
            f.write("\n")


if __name__ == "__main__":
    main()
