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
DIMENSIONS = int(os.getenv("DIMENSIONS", "500"))
NUMBER_OF_CENTERS = int(os.getenv("NUMBER_OF_CENTERS", "20"))
NUMBER_OF_ITERATIONS = int(os.getenv("NUMBER_OF_ITERATIONS", "10"))
NUMBER_OF_KMEANS_ITERATIONS = int(os.getenv("NUMBER_OF_KMEANS_ITERATIONS", "10"))
EXEC_IN_NVRAM = bool(int(os.getenv("EXEC_IN_NVRAM", "0")))

SEED = 42
MODE = 'uniform'

#############################################
#############################################
def recompute_centers(partials):
    aggr = np.sum(partials, axis=0)

    centers = list()
    for sum_ in aggr:
        # centers with no elements are removed
        if sum_[1] != 0:
            centers.append(sum_[0] / sum_[1])
    return np.array(centers)


def kmeans_frag(fragments):
    centers = np.matrix(
        [np.random.random(DIMENSIONS) for _ in range(NUMBER_OF_CENTERS)]
    )

    for it in range(NUMBER_OF_KMEANS_ITERATIONS):
        print("Doing k-means iteration #%d/%d" % (it + 1, NUMBER_OF_KMEANS_ITERATIONS))

        partials = list()
        for frag in fragments:
            partial = frag.partial_sum(centers)
            partials.append(partial)

        centers = recompute_centers(partials)
        # Ignoring any convergence criteria --always doing all iterations for timing purposes.

    return centers


def main():

    print(f"""Starting experiment with the following:

POINTS_PER_FRAGMENT = {POINTS_PER_FRAGMENT}
NUMBER_OF_FRAGMENTS = {NUMBER_OF_FRAGMENTS}
DIMENSIONS = {DIMENSIONS}
NUMBER_OF_CENTERS = {NUMBER_OF_CENTERS}
NUMBER_OF_ITERATIONS = {NUMBER_OF_ITERATIONS}
NUMBER_OF_KMEANS_ITERATIONS = {NUMBER_OF_KMEANS_ITERATIONS}
EXEC_IN_NVRAM = {EXEC_IN_NVRAM}
""")
    start_time = time.time()

    # Generate the data
    fragment_list = []

    for i in range(NUMBER_OF_FRAGMENTS):
        print("Generating fragment #%d" % (i + 1))
        
        fragment = Fragment()
        fragment.make_persistent()
        fragment.generate_points(POINTS_PER_FRAGMENT, DIMENSIONS, MODE, SEED + i)

        if EXEC_IN_NVRAM:
            fragment.persist_to_nvram()

        fragment_list.append(fragment)

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

        centers = kmeans_frag(fragments=fragment_list)

        end_t = time.time()

        kmeans_time = end_t - start_t
        print("k-means time (#%d/%d): %f" % (i + 1, NUMBER_OF_ITERATIONS, kmeans_time))

        result_times.append(kmeans_time)

    print("Ending kmeans")

    with open("results_app.csv", "a") as f:
        for result in result_times:
            # Mangling everything with a ",".join
            content = ",".join([
                str(POINTS_PER_FRAGMENT),
                str(NUMBER_OF_FRAGMENTS),
                str(DIMENSIONS),
                str(NUMBER_OF_CENTERS),
                str(NUMBER_OF_KMEANS_ITERATIONS),
                str(int(EXEC_IN_NVRAM)),
                "?", # MODE, researcher MUST set it
                str(result)
            ])
            f.write(content)
            f.write("\n")


if __name__ == "__main__":
    main()
    api.finish()
