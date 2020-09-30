#!/bin/bash

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
    export POINTS_PER_FRAGMENT=200000
    export NUMBER_OF_FRAGMENTS=16

    initialize_dataclay
    $COMMAND
    teardown_dataclay

    export POINTS_PER_FRAGMENT=4000
    export NUMBER_OF_FRAGMENTS=800

    initialize_dataclay
    $COMMAND
    teardown_dataclay
}

function big_experiments() {
    export POINTS_PER_FRAGMENT=200000
    export NUMBER_OF_FRAGMENTS=64

    initialize_dataclay
    $COMMAND
    teardown_dataclay

    export POINTS_PER_FRAGMENT=4000
    export NUMBER_OF_FRAGMENTS=3200

    initialize_dataclay
    $COMMAND
    teardown_dataclay
}

trap teardown_dataclay EXIT
COMMAND="numactl -N 1 -m 1 python kmeans_dcnonactive.py"

##########################################################

small_experiments
big_experiments
