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
