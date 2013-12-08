
import sys, random

#1 start and end time 
#2 job ID 
#3 task index 
#4 machine ID 
#5 CPU usage (aka rate) - mean 
#6 memory usage 
#7 assigned memory 
#8 unmapped page cache memory usage 
#9 page cache memory usage
#10 maximum memory usage 
#11 disk I/O time - mean 
#12 local disk space used - mean 
#13 CPU usage (aka rate) - max 
#14 disk IO time - max 
#15 cycles per instruction (CPI) 
#16 memory accesses per instruction (MAI) 
#17 sampling rate 
#18 aggregation type

# task.start_time  = float(self.line[0])/1000000.
# task.end_time    = float(self.line[1])/1000000.
# task.job_ID      = int(self.line[2])
# task.task_ID     = int(self.line[3])
# task.machine_ID  = -1 # int(self.line[4])
# task.CPU_usage   = float(self.line[5])
# task.mem_usage   = float(self.line[10])
# task.age_round   = 0

folder       = sys.argv[1]
numVMs       = int(sys.argv[2])
numIntervals = int(sys.argv[3])

interval     = 300.

fp = open(folder + "/part-00000-of-00500.csv", "w+")

for i in range(0, numIntervals):

	for v in range(0, numVMs):

		lst = [0] * 19

		lst[0] = (interval * i + 1) * 1000000.
		lst[1] = (interval * (i + 1)) * 1000000.

		lst[2] = 1
		lst[3] = 1000 + v

		lst[5] = random.random()
		lst[10] = random.random()

		ln = ""
		for l in lst:
			ln = ln + str(l) + ","

		fp.write(ln + "\n")

fp.close()