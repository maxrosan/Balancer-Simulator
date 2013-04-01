#!/bin/bash

#configs=("config_vars_04.py" "config_vars_06.py" "config_vars_08.py" "config_vars_1.py")

#configs=("config_tasks_log_brucutu.py" "config_vars_06_brucutu.py" "config_vars_1_brucutu.py" "config_vars_04_brucutu.py" "config_vars_08_brucutu.py")

configs=("config/toyoda/config_vars_04_brucutu.py" "config/ffd/config_vars_04_ffd_brucutu.py")

for cfg in ${configs[*]}; do
	~/brucutu/pypy-c-jit-59498-b03871503962-linux/bin/pypy ./main.py config/$cfg;
done;
