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
}

function small_experiments() {
    export POINTS_PER_FRAGMENT=200000
    export NUMBER_OF_FRAGMENTS=16

    initialize_container
    $COMMAND
    teardown_container

    export POINTS_PER_FRAGMENT=4000
    export NUMBER_OF_FRAGMENTS=800

    initialize_container
    $COMMAND
    teardown_container
}

function big_experiments() {
    export POINTS_PER_FRAGMENT=200000
    export NUMBER_OF_FRAGMENTS=64

    initialize_container
    $COMMAND
    teardown_container

    export POINTS_PER_FRAGMENT=4000
    export NUMBER_OF_FRAGMENTS=3200

    initialize_container
    $COMMAND
    teardown_container
}

trap teardown_container EXIT
COMMAND="numactl -N 1 -m 1 python kmeans_daos.py"

export DAOS_POOL
export DAOS_CONT

##########################################################
export NUMBER_OF_KMEANS_ITERATIONS=10
export NUMBER_OF_CENTERS=20
export NUMBER_OF_ITERATIONS=10
export DIMENSIONS=500
##########################################################

small_experiments
big_experiments
