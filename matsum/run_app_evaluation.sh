#!/bin/bash

# Set this to true for AD mode, false for Memory Mode
SET_NVRAM_FLAGS=true

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
    export BLOCKSIZE=1000
    export MATRIXSIZE=42

    initialize_dataclay
    $COMMAND
    teardown_dataclay

    export BLOCKSIZE=7000
    export MATRIXSIZE=6

    initialize_dataclay
    $COMMAND
    teardown_dataclay   
}

function big_experiments() {
    export BLOCKSIZE=1000
    export MATRIXSIZE=84

    initialize_dataclay
    $COMMAND
    teardown_dataclay

    export BLOCKSIZE=7000
    export MATRIXSIZE=12

    initialize_dataclay
    $COMMAND
    teardown_dataclay
}

trap teardown_dataclay EXIT
COMMAND="numactl -N 1 -m 1 python matsum.py"


##########################################################
export NUMBER_OF_ITERATIONS=10
##########################################################
export INPUT_IN_NVRAM=0
export RESULT_IN_NVRAM=0

small_experiments

##########################################################
if [ "$SET_NVRAM_FLAGS" = true ] ; then
export INPUT_IN_NVRAM=1
export RESULT_IN_NVRAM=0

# Repeat the small experiments
small_experiments
fi
##########################################################

big_experiments

##########################################################
if [ "$SET_NVRAM_FLAGS" = true ] ; then
export INPUT_IN_NVRAM=1
export RESULT_IN_NVRAM=1

# Repeat all previous experiments (but now with RESULT_IN_NVRAM flag set)
small_experiments
big_experiments
fi
##########################################################
