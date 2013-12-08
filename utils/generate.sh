#!/bin/bash

DIR=$1
NUM=$2

if [ ! -e $DIR ]; then
	mkdir -p $DIR;
	mkdir -p $DIR/task_usage;
	mkdir -p $DIR/machine_events;
	mkdir -p $DIR/log;
fi;

python utils/generate_trace.py $DIR/task_usage/ $NUM 10
python utils/generate_constant_machines.py $DIR/machine_events $NUM