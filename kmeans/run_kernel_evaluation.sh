#!/bin/bash

##########################################################
# Be sure to check TEST_OVERFILL_CONFIG and 
# TEST_IN_NVRAM_CONFIG flags before using this!
#
# Their value should match the desired test and the mode
# of the system.
##########################################################

# This flag makes sense for Memory Mode
TEST_OVERFILL_CONFIG=false

# This only works with App Direct available devices
TEST_IN_NVRAM_CONFIG=true

COMMAND="numactl -N 0 -m 0 python kernel_eval.py"

##########################################################
export NUMBER_OF_CENTERS=20
export DIMENSIONS=500
##########################################################
export EXEC_IN_NVRAM=0

export POINTS_PER_FRAGMENT=200000
export NUMBER_OF_ITERATIONS=20
export NUMBER_OF_GENERATIONS=20

$COMMAND

export POINTS_PER_FRAGMENT=4000
export NUMBER_OF_ITERATIONS=40
export NUMBER_OF_GENERATIONS=40

$COMMAND


##########################################################
if [ "$TEST_OVERFILL_CONFIG" = true ] ; then
##########################################################
export EXEC_IN_NVRAM=0

export POINTS_PER_FRAGMENT=200000
export NUMBER_OF_ITERATIONS=200
export NUMBER_OF_GENERATIONS=250

$COMMAND

export POINTS_PER_FRAGMENT=4000
export NUMBER_OF_ITERATIONS=400
export NUMBER_OF_GENERATIONS=125000

$COMMAND

fi
##########################################################

##########################################################
if [ "$TEST_IN_NVRAM_CONFIG" = true ] ; then
##########################################################
export EXEC_IN_NVRAM=1

export POINTS_PER_FRAGMENT=200000
export NUMBER_OF_ITERATIONS=20
export NUMBER_OF_GENERATIONS=20

$COMMAND

export POINTS_PER_FRAGMENT=4000
export NUMBER_OF_ITERATIONS=40
export NUMBER_OF_GENERATIONS=40

$COMMAND

fi
##########################################################
