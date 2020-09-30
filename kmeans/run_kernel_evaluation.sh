#!/bin/bash

##########################################################
# Typically, you will call this with a tee pipe, i.e.:
#
# $ bash run_kernel_evaluation.sh | tee logs.log
#
# As the output may be a little bit verbose and you will want
# to process the data afterwards.
# 
# Be sure to check TEST_OVERFILL_CONFIG and 
# TEST_IN_NVRAM_CONFIG flags before using this!
#
# Their value should match the desired test and the mode
# of the system.
##########################################################

# This flag makes sense for Memory Mode
TEST_OVERFILL_CONFIG=true

# This only works with App Direct available devices
TEST_IN_NVRAM_CONFIG=false

COMMAND="numactl -N 0 -m 0 python kernel_eval.py"

##########################################################
export NUMBER_OF_CENTERS=20
export DIMENSIONS=500
##########################################################
export EXEC_IN_NVRAM=0

export POINTS_PER_FRAGMENT=200000
export NUMBER_OF_ITERATIONS=10
export NUMBER_OF_GENERATIONS=10

$COMMAND

export POINTS_PER_FRAGMENT=4000
export NUMBER_OF_ITERATIONS=40
export NUMBER_OF_GENERATIONS=20

$COMMAND


##########################################################
if [ "$TEST_OVERFILL_CONFIG" = true ] ; then
##########################################################
export EXEC_IN_NVRAM=0

export POINTS_PER_FRAGMENT=200000
export NUMBER_OF_ITERATIONS=10
export NUMBER_OF_GENERATIONS=100

$COMMAND

export POINTS_PER_FRAGMENT=4000
export NUMBER_OF_ITERATIONS=40
export NUMBER_OF_GENERATIONS=5000

$COMMAND

fi
##########################################################

##########################################################
if [ "$TEST_IN_NVRAM_CONFIG" = true ] ; then
##########################################################
export EXEC_IN_NVRAM=1

export POINTS_PER_FRAGMENT=200000
export NUMBER_OF_ITERATIONS=10
export NUMBER_OF_GENERATIONS=10

$COMMAND

export POINTS_PER_FRAGMENT=4000
export NUMBER_OF_ITERATIONS=40
export NUMBER_OF_GENERATIONS=20

$COMMAND

fi
##########################################################
