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
    export POINTS_PER_FRAGMENT=100000000
    export NUMBER_OF_FRAGMENTS=32

    initialize_container
    $COMMAND
    teardown_container

    export POINTS_PER_FRAGMENT=2000000
    export NUMBER_OF_FRAGMENTS=1600

    initialize_container
    $COMMAND
    teardown_container
}

function big_experiments() {
    export POINTS_PER_FRAGMENT=100000000
    export NUMBER_OF_FRAGMENTS=256

    initialize_container
    $COMMAND
    teardown_container

    export POINTS_PER_FRAGMENT=2000000
    export NUMBER_OF_FRAGMENTS=12800

    initialize_container
    $COMMAND
    teardown_container
}

COMMAND="numactl -N 1 -m 1 python histogram_daos.py"

export DAOS_POOL
export DAOS_CONT

##########################################################
export NUMBER_OF_ITERATIONS=10

small_experiments
big_experiments
