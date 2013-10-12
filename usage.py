#!/usr/bin/pypy

import io, sys, os, commands

class TaskUsageRegister:

	start_time = 0.0
	end_time   = 0.0
	job_ID     = 0
	task_ID    = 0
	machine_ID = 0
	CPU_usage  = 0.0
	mem_usage  = 0.0
	age_round  = 0
	last_round = 0
	altererd   = False
	move       = False
	mig_origin = -1
	CPU_usage_real = 0.
	mem_usage_real = 0.
	machine_trace  = -1

	def TaskUsageRegister(self):

	def updateWithRealValues(self):
		self.CPU_usage = self.CPU_usage_real
		self.mem_usage = self.mem_usage_real

	def getID(self):
		return (str(self.job_ID) + "." + str(self.task_ID))

	def __hash__(self):
		return self.getID()

	def __eq__(self, other):
		return ((self.job_ID == other.job_ID) and (self.task_ID == other.task_ID))

	def __str__(self):
		return  "[%d %d [%d/%d] %.5f %.5f]" % (self.start_time, self.end_time, self.job_ID, self.task_ID, self.CPU_usage, self.mem_usage)

	def print_info(self):
		print "%d %d [%d/%d] %.5f %.5f" % (self.start_time, self.end_time, self.job_ID, self.task_ID, self.CPU_usage, self.mem_usage)

	def inc_age(self):
		self.age_round = self.age_round + 1

class TaskUsage:

	def __init__(self, folder, part):
		self.line = None
		self.folder = folder
		self.part = part - 1
		self.fd = None
		self.num_lines = 0
	
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

		self.num_lines = self.num_lines + 1


	def search_for_instant(self, instant):
		part = 0

		op = commands.getstatusoutput('tail -n 1 ' + self.name_format(part))
		while op[0] == 0:
			start_time = float(op[1].split(',',18)[0])/1000000.
			if start_time > instant:
				return part
			else:
				part = part + 1
				op = commands.getstatusoutput('tail -n 1 ' + self.name_format(part))

		return -1
		
		
	def read_until(self, start, end, callback, arg): # callback(arg, TaskUsageRegister)

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
				task.start_time  = float(self.line[0])/1000000.
				task.end_time    = float(self.line[1])/1000000.
				task.job_ID      = int(self.line[2])
				task.task_ID     = int(self.line[3])
				task.machine_ID  = -1 # int(self.line[4])
				task.CPU_usage   = float(self.line[5])
				task.mem_usage   = float(self.line[10])
				task.age_round   = 0
				task.last_round  = -1
				task.first_round = 0
				task.altered     = False
				task.move        = False
				task.mig_origin  = -1

				task.machine_trace  = int(self.line[4])
				task.CPU_usage_real = task.CPU_usage
				task.mem_usage_real = task.mem_usage

				if start <= task.start_time and task.end_time <= end:
					callback(arg, task)
					self.line = None				
				else:
					keep_going = False
	
		return True

if __name__ == "__main__":

	#def task_info(arg, task):
	#	task.print_info()
	
	taskuse = TaskUsage(sys.argv[1], 0)
	#taskuse.read_until(5613., task_info, None)

	print taskuse.search_for_instant(51900)
