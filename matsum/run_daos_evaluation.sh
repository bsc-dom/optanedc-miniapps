#!/bin/bash

function initialize_container() {
    echo "Initializing DAOS container on pool $DAOS_POOL"

    # Is there a smarter way of parsing? Maybe. Bash is ugly.
    RET=`daos cont create --pool=$DAOS_POOL --svc=0`
    read -ra FIELDS <<< $RET
    export DAOS_CONT=${FIELDS[-1]}
}

function teardown_container() {
    echo "Destroying DAOS container $DAOS_CONT on pool $DAOS_POOL"

    daos cont destroy --force --svc=0 --cont=$DAOS_CONT --pool=$DAOS_POOL

    # Those logs tends to grow indefinetely and break things
    rm /tmp/daos*.log
}

function small_experiments() {
    export BLOCKSIZE=1000
    export MATRIXSIZE=42

    initialize_container
    $COMMAND
    teardown_container

    export BLOCKSIZE=7000
    export MATRIXSIZE=6

    initialize_container
    $COMMAND
    teardown_container
}

function big_experiments() {
    export BLOCKSIZE=1000
    export MATRIXSIZE=84

    initialize_container
    $COMMAND
    teardown_container

    export BLOCKSIZE=7000
    export MATRIXSIZE=12

    initialize_container
    $COMMAND
    teardown_container
}

trap teardown_container EXIT
COMMAND="numactl -N 1 -m 1 python matsum_daos.py"

export DAOS_POOL
export DAOS_CONT

##########################################################
export NUMBER_OF_ITERATIONS=10

export RESULT_IN_NVRAM=0

small_experiments
big_experiments

export RESULT_IN_NVRAM=1

small_experiments
big_experiments
