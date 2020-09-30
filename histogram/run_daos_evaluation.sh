#!/bin/bash

function small_experiments() {
    #export POINTS_PER_FRAGMENT=100000000
    #export NUMBER_OF_FRAGMENTS=16
    #export NUMBER_OF_ITERATIONS=10

    #$COMMAND

    export POINTS_PER_FRAGMENT=2000000
    export NUMBER_OF_FRAGMENTS=800
    export NUMBER_OF_ITERATIONS=10

    $COMMAND
}

function big_experiments() {
    export POINTS_PER_FRAGMENT=100000000
    export NUMBER_OF_FRAGMENTS=64
    export NUMBER_OF_ITERATIONS=10

    $COMMAND

    export POINTS_PER_FRAGMENT=2000000
    export NUMBER_OF_FRAGMENTS=3200
    export NUMBER_OF_ITERATIONS=10

    $COMMAND
}

COMMAND="numactl -N 1 -m 1 python histogram_daos.py"

export DAOS_POOL
export DAOS_CONT

##########################################################

small_experiments
big_experiments
