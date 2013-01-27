#!/usr/bin/pypy

import io, sys, os

class TaskUsageRegister:

	def TaskUsageRegister(self):
		self.start_time = 0.0
		self.end_time   = 0.0
		self.job_ID     = 0
		self.task_ID    = 0
		self.machine_ID = 0
		self.CPU_usage  = 0.0
		self.mem_usage  = 0.0

	def __hash__(self):
		return ((self.job_ID << 64) + self.task_ID) # python trata isso 

	def __eq__(self, other):
		return ((self.job_ID == other.job_ID) and (self.task_ID == other.task_ID))

	def print_info(self):
		print "%d %d [%d/%d] %.5f %.5f" % (self.start_time, self.end_time, self.job_ID, self.task_ID, self.CPU_usage, self.mem_usage)

class TaskUsage:

	def __init__(self, folder, part):
		self.line = None
		self.folder = folder
		self.part = part - 1
		self.fd = None
	
	def name_format(self, part):
		num_str = str(part)
		fn = self.folder + "/part-" + ("0" * (5 - len(num_str))) + num_str + "-of-00500.csv"
		return fn
	
	def has_next(self):
		fn = self.name_format(self.part + 1)
		return os.path.exists(fn)		

	def open_next(self):
		self.part = self.part + 1
		self.fd = io.open(self.name_format(self.part), 'r+')

		print "Arquivo " + str(self.part) + " do task usage"

	def dect_eof(self):
		return (self.line == None)

	def read_next_line(self):
		if self.fd == None:
			self.line = None
			return

		ln = self.fd.readline()
		if len(ln) < 1 or (not ln.endswith("\n")):
			self.line = None
		else:
			self.line = ln.split(',',18)
		
	def read_until(self, instant, callback, arg): # callback(arg, TaskUsageRegister)

		keep_going = True

		while keep_going:

			if self.line == None:
				self.read_next_line()

			if self.dect_eof():
				if self.has_next():
					self.open_next() # considera-se que o proximo arquivo tenha pelo menos uma linha
				else:
					keep_going = False
			else:
				task = TaskUsageRegister()
				task.start_time = float(self.line[0])/1000000.
				task.end_time   = float(self.line[1])/1000000.
				task.job_ID     = int(self.line[2])
				task.task_ID    = int(self.line[3])
				task.machine_ID = int(self.line[4])
				task.CPU_usage  = float(self.line[5])
				task.mem_usage  = float(self.line[6])

				if (task.start_time <= instant):
					callback(arg, task)
					self.line = None				
				else:
					keep_going = False
		
		return True

if __name__ == "__main__":

	def task_info(arg, task):
		task.print_info()
	
	taskuse = TaskUsage(sys.argv[1], 0)
	taskuse.read_until(5613., task_info, None)
