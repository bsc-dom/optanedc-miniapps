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

## Kernel evaluation

Each application has a `kernel_eval.py` script that can be used in order to evaluate the isolated performance of the kernel routines in different scenarios.

You will need to set up the appropriate environment variables per each application and per each scenario evaluation.

**Caution!** Memory Mode may be tricky to evaluate and probably you may want to consider two different scenarios: fits-in-DRAM and does-not-fit-in-DRAM. You can force each of those two scenarios by changing the `NUMBER_OF_ITERATIONS` environment variable.

## Analysis

There is a folder `analysis` where there are some Jupyter notebooks used for analysis and
figures generation.

You will need to install install `jupyter` and `seaborn` in order to use it.

The notebooks expect to find a csv file with the results, in that same folder. The column names 
for the csv will depend for each application but in all of them you will need to include the 
dataset size and the _mode_ (e.g. `ad-wram` or `mm`).

# Usage of DAOS -- Optane DC

## Prerequisites

Install DAOS and its Python bindings. You may follow the 
[official documentation](https://daos-stack.github.io/admin/installation/)
and be sure that at the end you have the Python module installed. You may need
to update your `PYTHONPATH` environment variable (YMMV).

## Preparing the configuration

We will be using a DCPM-only configuration of DAOS --as this will
result in a meaningful and fair comparison. You should tweak the
configuration files for DAOS into something like the following:

```yaml
# daos_server.yaml

# (...)

transport_config:
   allow_insecure: true

socket_dir: # <-- default /var/run only while using root!

servers:
  - #(...)
    scm_class: dcpm
    # Update according to your hardware/OS configuration:
    scm_mount: /mnt/daos0 # map to -s /mnt/daos
    scm_list: [/dev/pmem0.2]
```

```yaml
# daos_agent.yaml
runtime_dir: # <-- default /var/run only while using root!
             # (match the one in daos_server.yml)
```

## Starting the DAOS stack

Do the following:

```
$ daos_server start -o install/etc/daos_server.yml
$ dmg -i storage prepare
$ dmg -i storage format
$ daos_agent -i -o install/etc/daos_agent.yml
```

If you are restarting the stack, you may need to skip the `prepare` step and instead change the format into `dmg storage -i format --reformat`. Also you may need to clean up files from `/mnt/daos0`. Keep all that in mind. 

I recommend using tmux/screen/byobu or similar to keep both `daos_server` and `daos_agent` commands running in foreground/persistent --you don't want them to be killed due to ssh/network hiccups on your side.

## Preparing the _pool_ and the _container_

Before starting the Python applications, you need to define pool and container. I will be using the daos management tool. First, the _pool_:

```
$ dmg pool create -i --scm-size=800G --nvme-size=0G
```

As stated above, it will be a DCPM-only setup, thus the `nvme-size=0` parameter.

This, if succeeds, will spit a UUID for the created pool. Example output:

```
Pool-create command SUCCEEDED: UUID: d8c2786c-75e4-4fd3-914c-a76c49d10676, Service replicas: 0
```

**The scripts manage the container by themselves, the following steps are not required
for typical application benchmarking**

Then use it to create the _container_:

```
$ daos cont create --pool=d8c2786c-75e4-4fd3-914c-a76c49d10676 --svc=0
Successfully created container 886a015d-aa9b-4f77-b94b-ea750b6fbaa1
```

Export the variables and you are ready to start the applications:

```
$ export DAOS_POOL=d8c2786c-75e4-4fd3-914c-a76c49d10676
# DAOS_CONT is not required, current scripts manage those
$ export DAOS_CONT=886a015d-aa9b-4f77-b94b-ea750b6fbaa1
```

Of course, you will need to change all the UUID to use the ones that you get.

## Start the applications

Ensure that you have `DAOS_POOL` environment defined (check `env`) and ensure that `daos` python module is available (`import pydaos` in a Python interpreter should not give an `ImportError`).

Each application has a `<app_name>_daos.py` Python application that runs the application. E.g.:

```
$ cd apps/matsum
$ python matsum_daos.py
Starting experiment with the following:
(...)
-----------------------------------------
-------------- RESULTS ------------------
-----------------------------------------
Initialization time: ###.######
Matsum time: ###.######
-----------------------------------------
```
