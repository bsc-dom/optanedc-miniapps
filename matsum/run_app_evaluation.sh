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
    export BLOCKSIZE=1000
    export MATRIXSIZE=24

    initialize_dataclay
    $COMMAND
    teardown_dataclay

    export BLOCKSIZE=4000
    export MATRIXSIZE=6

    initialize_dataclay
    $COMMAND
    teardown_dataclay   
}

function medium_experiments() {
    export BLOCKSIZE=1000
    export MATRIXSIZE=48

    initialize_dataclay
    $COMMAND
    teardown_dataclay

    export BLOCKSIZE=4000
    export MATRIXSIZE=12

    initialize_dataclay
    $COMMAND
    teardown_dataclay
}

function big_experiments() {
    export BLOCKSIZE=1000
    export MATRIXSIZE=96

    initialize_dataclay
    $COMMAND
    teardown_dataclay

    export BLOCKSIZE=4000
    export MATRIXSIZE=24

    initialize_dataclay
    $COMMAND
    teardown_dataclay
}

trap teardown_dataclay EXIT
COMMAND="numactl -N 1 -m 1 python matsum.py"


##########################################################
export NUMBER_OF_ITERATIONS=10
##########################################################
export EXEC_IN_NVRAM=0
export RESULT_IN_NVRAM=0

small_experiments

##########################################################
if [ "$SET_EXEC_IN_NVRAM_FLAG" = true ] ; then
export EXEC_IN_NVRAM=1
export RESULT_IN_NVRAM=0

# Repeat the small experiments
small_experiments
fi
##########################################################

medium_experiments

##########################################################
if [ "$SET_EXEC_IN_NVRAM_FLAG" = true ] ; then
export EXEC_IN_NVRAM=1
export RESULT_IN_NVRAM=1

# Repeat all previous experiments (but now with RESULT_IN_NVRAM flag set)
small_experiments
medium_experiments
fi
##########################################################

# Finally, the big experiments
# (Note that RESULT_IN_NVRAM will have the valid state at this point!)
big_experiments