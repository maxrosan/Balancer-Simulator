#!/bin/sh

#ssocr -d 4 crop 526 150 360 250 -t 30 remove_isolated closing 1  op/video1.jpg -o op/op.jpg

rm results.txt;
touch results.txt;

sec=0.0
last=0

for i in `ls $1 | sort -n -t o -k 2`; do
	file=$i;
	#result=`ssocr -d -1 -t 30 crop 526 150 360 250 remove_isolated rotate 2 remove_isolated closing 2 op/${file} -o op/op.jpg`;
	#result=`ssocr -d 4 crop 250 150 360 250 -t 30 rotate 2 remove_isolated closing 2  op2/$file -o op2/op.jpg`
	#result=`ssocr -d 4 crop 385 230 360 220 -t 25 remove_isolated closing 2  op/$file -o op/op.jpg`
	#result=`ssocr -d 4 crop 350 230 360 220 -t 25 remove_isolated closing 2  op/$file -o op/op.jpg`
	#result=`ssocr -d -1 crop 350 310 360 220 -t 40 grayscale dilation remove_isolated  op/$file -o op/op.jpg`
	#result=`ssocr -d -1 crop 660 310 250 180 -t 40 rotate 4 grayscale op/$file -o op/op.jpg`
	#result=`ssocr -d -1 crop 630 310 280 180 -t 30 grayscale dilation remove_isolated op/$file -o op/op.jpg`
	#result=`ssocr -d -1 crop 350 23 250 180 -t 40 rotate 355 dilation op/$file -o op/op.jpg`
	result=`ssocr -d -1 crop 366 200 330 222 $1/$file -o tmp/op.jpg`
	#echo "$file : $result" >> results.txt;
	if [[ $result =~ ^[0-9]+[.][0-9]$ ]]; then
		echo "ok $sec $file ($result)";
		last=$result
	else
		echo "fail $file ($result)";
		result=$last
	fi;
	echo "$sec $result" >> results.txt
	sec=`echo "$sec+0.15" | bc`
done;

