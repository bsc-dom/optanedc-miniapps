#!/bin/bash

# Set this to true for AD mode, false for Memory Mode
SET_EXEC_IN_NVRAM_FLAG=true

function initialize_dataclay() {
    pushd ~/dataclay
    ./cleanUp.sh
    ./startServices.sh &> ~/dataclay.log &
    DATACLAY_PID=$!
    sleep 30

    popd
    ./register.sh
}

function teardown_dataclay() {
    echo "Killing Java and Python processes"
    # Ugly but... I want to make sure that all processes are indeed dead
    # (and I do not care about disk persistency)
    killall -9 java
    killall -9 python
}

function small_experiments() {
    export POINTS_PER_FRAGMENT=100000000
    export NUMBER_OF_FRAGMENTS=32
    export NUMBER_OF_ITERATIONS=10

    initialize_dataclay
    $COMMAND
    teardown_dataclay

    export POINTS_PER_FRAGMENT=2000000
    export NUMBER_OF_FRAGMENTS=1600
    export NUMBER_OF_ITERATIONS=10

    initialize_dataclay
    $COMMAND
    teardown_dataclay
}

function big_experiments() {
    export POINTS_PER_FRAGMENT=100000000
    export NUMBER_OF_FRAGMENTS=256

    initialize_dataclay
    $COMMAND
    teardown_dataclay

    export POINTS_PER_FRAGMENT=2000000
    export NUMBER_OF_FRAGMENTS=12800

    initialize_dataclay
    $COMMAND
    teardown_dataclay
}

trap teardown_dataclay EXIT
COMMAND="numactl -N 1 -m 1 python histogram.py"

export NUMBER_OF_ITERATIONS=10
##########################################################
export EXEC_IN_NVRAM=0

small_experiments
##########################################################
if [ "$SET_EXEC_IN_NVRAM_FLAG" = true ] ; then
export EXEC_IN_NVRAM=1

# Repeat small experiments
small_experiments
fi
##########################################################

# Proceed to bigger experiments
big_experiments
