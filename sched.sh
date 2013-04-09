#!/bin/bash
##

#configs=("config_vars_04.py" "config_vars_06.py" "config_vars_08.py" "config_vars_1.py")
configs=("config/test/test_knapsack.py", "config/test/test_ffd.py")

for cfg in ${configs[*]}; do
	HOST=`hostname`

	if [ "x$HOST" == "xgodzilla" ]; then
		~/simulator/pypy/pypy-c-jit-59498-b03871503962-linux/bin/pypy ./main.py $cfg;
	else
		pypy ./main.py $1;
	fi;
done;
