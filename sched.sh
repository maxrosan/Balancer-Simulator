#!/bin/sh

#configs=("config_vars_04.py" "config_vars_06.py" "config_vars_08.py" "config_vars_1.py")

for cfg in ${configs[*]}; do
	~/simulator/pypy/pypy-c-jit-59498-b03871503962-linux/bin/pypy ./main.py $cfg;
done;
