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
export EXEC_IN_NVRAM=0

export BLOCKSIZE=4000
export NUMBER_OF_ITERATIONS=20
export NUMBER_OF_GENERATIONS=10

$COMMAND

export BLOCKSIZE=1000
export NUMBER_OF_ITERATIONS=40
export NUMBER_OF_GENERATIONS=20

$COMMAND

##########################################################
if [ "$TEST_OVERFILL_CONFIG" = true ] ; then
##########################################################
export EXEC_IN_NVRAM=0

export BLOCKSIZE=4000
export NUMBER_OF_ITERATIONS=20
export NUMBER_OF_GENERATIONS=150

$COMMAND

export BLOCKSIZE=1000
export NUMBER_OF_ITERATIONS=40
export NUMBER_OF_GENERATIONS=5000

$COMMAND

fi
##########################################################

##########################################################
if [ "$TEST_IN_NVRAM_CONFIG" = true ] ; then
##########################################################
export EXEC_IN_NVRAM=1

export BLOCKSIZE=4000
export NUMBER_OF_ITERATIONS=20
export NUMBER_OF_GENERATIONS=10

$COMMAND

export BLOCKSIZE=1000
export NUMBER_OF_ITERATIONS=40
export NUMBER_OF_GENERATIONS=20

$COMMAND

fi
##########################################################
