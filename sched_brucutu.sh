#!/bin/bash

#configs=("config_vars_04.py" "config_vars_06.py" "config_vars_08.py" "config_vars_1.py")

configs=("config_interval_05.py" "config_interval_10.py" "config_interval_20.py" "config_interval_40.py" "config_interval_80.py")

for cfg in ${configs[*]}; do
	~/brucutu/pypy-c-jit-59498-b03871503962-linux/bin/pypy ./main.py config/$cfg;
done;
