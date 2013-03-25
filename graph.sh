#!/bin/sh -xe

# $1 file

# 			self.balancing_fobj.write("%d %d %d %d %d %d %d %f %f %f %f %f %d %d\n" % (
#				self.n_round ( 1 ),
#				self.task_mapped_successfully ( 2 ) , self.task_failed_to_map ( 3 ),
#			 	self.machines_used ( 4 ) , self.machines_not_used ( 5 ),
#				self.n_migrations ( 6 ),
#				self.task_new ( 7 ),
#				self.total_time ( 8 ),
#				self.usage_mean_per ( 9 ), self.usage_stan_per ( 10 ),
#				self.usage_CPU_mean ( 11 ), self.usage_mem_mean ( 12 ),
#				self.total_tasks ( 13 ),
#				self.SLA_breaks ( 14 )))

FILE=$1
TITLE=$2

FILE_TO_CMP=$3
TITLE_CMP=$4

COL=$5

OUTPUT="${FILE}.svg"

if [ -e $OUTPUT ]; then
	rm $OUTPUT
fi;

gnuplot -e "set output \"${OUTPUT}\"; set terminal svg; \
	    plot \"${FILE}\" using 1:$COL title \"${TITLE}\" with lines, \"${FILE_TO_CMP}\" using 1:$COL title \"${TITLE_CMP}\" with lines "
