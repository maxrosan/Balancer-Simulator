#!/bin/sh -xe


TIME=60

#perf stat -o log/out_0.txt ./a.out 0 $TIME

#echo "Continue?"
#read CONTINUE

for ((i = 6 * 1024; i <= 6 * 1024; i = i * 2)); do

	echo "MEM = $i MB"
	perf stat -o log/out_$i.txt ./a.out $i $TIME

	echo "Continue?"
	read CONTINUE

done;
