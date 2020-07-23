# optanedc-miniapps
Applications for Optane DC evaluation with dataClay

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
$ dmg pool create -i --scm-size=200G --nvme-size=0G
```

As stated above, it will be a DCPM-only setup, thus the `nvme-size=0` parameter.

This, if succeeds, will spit a UUID for the created pool. Example output:

```
Pool-create command SUCCEEDED: UUID: d8c2786c-75e4-4fd3-914c-a76c49d10676, Service replicas: 0
```

Then use it to create the _container_:

```
$ daos cont create --pool=d8c2786c-75e4-4fd3-914c-a76c49d10676 --svc=0
Successfully created container 886a015d-aa9b-4f77-b94b-ea750b6fbaa1
```

Export the variables and you are ready to start the applications:

```
$ export DAOS_POOL=d8c2786c-75e4-4fd3-914c-a76c49d10676
$ export DAOS_CONT=886a015d-aa9b-4f77-b94b-ea750b6fbaa1
```

Of course, you will need to change all the UUID to use the ones that you get.

## Start the applications

Ensure that you have `DAOS_POOL` and `DAOS_CONT` environment defined (check `env`) and ensure that `daos` python module is available (`import pydaos` in a Python interpreter should not give an `ImportError`).

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
