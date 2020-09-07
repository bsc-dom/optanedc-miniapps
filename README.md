# optanedc-miniapps
Applications for Optane DC evaluation with [dataClay](https://dataclay.bsc.es/) active object store.

The following applications can be found in this repository:

 - `histogram` a histogram application
 - `kmeans` a _k_-means implementation using the standard algorithm
 - `matsum` a matrix addition
 - `matmul` a matrix multiplication

Note that all aplications are self-contained, meaning that the data is randomly
generated. The timing is based on calls to `time.time()` (wall clock time).

The NVM placement hints for the applications are done through the usage of the
[`npp2nvm` python library](https://github.com/bsc-dom/npp2nvm/).

## Registration of the data model

After initializing the dataClay stack, you need to register the data model. Each
`cfgfiles` folder contains a default configuration for the client which assumes
that dataClay is started at localhost.

Execution of the `register.sh` will register the data model in dataClay. Each application
has its own script. You will need to have the dataClay client libraries installed.

## Execution of the application

Each application folder has its own python main script. After completing the registration
of the data model you can execute the application by doing:

    $ python histogram.py

Change `histogram.py` depending on the application.

The application will generate the random data and execute the application. When the application
finishes, it will print in `stdout` the execution time.

If you need to change the dataset size, edit the python script and change the constants value (near
the beginning).

# Kernel evaluation

Each application has a `kernel_eval.py` script that can be used in order to evaluate the isolated performance of the kernel routines in different scenarios.

You will need to set up the appropriate environment variables per each application and per each scenario evaluation.

**Caution!** Memory Mode may be tricky to evaluate and probably you may want to consider two different scenarios: fits-in-DRAM and does-not-fit-in-DRAM. You can force each of those two scenarios by changing the `NUMBER_OF_ITERATIONS` environment variable.

# Analysis

There is a folder `analysis` where there are some Jupyter notebooks used for analysis and
figures generation.

You will need to install install `jupyter` and `seaborn` in order to use it.

The notebooks expect to find a csv file with the results, in that same folder. The column names 
for the csv will depend for each application but in all of them you will need to include the 
dataset size and the _mode_ (e.g. `ad-wram` or `mm`).
