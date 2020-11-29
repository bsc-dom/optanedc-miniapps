import time
import numpy as np
import os

from dataclay import api

api.init()

from model.fragment import Fragment


#############################################
# Constants / experiment values:
#############################################

POINTS_PER_FRAGMENT = int(os.environ["POINTS_PER_FRAGMENT"])
NUMBER_OF_FRAGMENTS = int(os.environ["NUMBER_OF_FRAGMENTS"])
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "10"))
EXEC_IN_NVRAM = bool(int(os.getenv("EXEC_IN_NVRAM", "0")))

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

        if EXEC_IN_NVRAM:
            frag.persist_to_nvram()
        
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

    print(f"""Starting experiment with the following:

POINTS_PER_FRAGMENT = {POINTS_PER_FRAGMENT}
NUMBER_OF_FRAGMENTS = {NUMBER_OF_FRAGMENTS}
NUMBER_OF_ITERATIONS = {NUMBER_OF_ITERATIONS}
EXEC_IN_NVRAM = {EXEC_IN_NVRAM}

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

    print("Ending histogram")
    print("-----------------------------------------")

    # Are we in Memory Mode?
    # Easy to know: check if there is more than 1TiB of memory
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    mem_tib = mem_bytes / (1024**4)
    mode = "MM" if mem_tib > 1 else "AD"

    with open("results_app.csv", "a") as f:
        for result in result_times:
            # Mangling everything with a ",".join
            content = ",".join([
                str(POINTS_PER_FRAGMENT),
                str(NUMBER_OF_FRAGMENTS),
                str(int(EXEC_IN_NVRAM)),
                mode,
                str(result)
            ])
            f.write(content)
            f.write("\n")


if __name__ == "__main__":
    main()
    api.finish()
