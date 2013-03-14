import loadbalacing
import numpypy as numpy
import math, random, Queue, io, operator

# RandomMethod selects a task randomly to run
#
class TasksStats(loadbalacing.LoadBalacing):

	def __init__(self, fileoutput, logoutput, n_writes_limit, len_hist_max):

		loadbalacing.LoadBalacing.__init__(self)

		self.tasks         = {}
		self.machines      = {}
		self.logf          = open(fileoutput, 'w+')
		self.hist          = {}
		self.logtask       = logoutput
		self.n_writes_lim  = n_writes_limit
		self.len_hist_max  = len_hist_max

		self.n_writes      = 0

	def __generate_output(self):

		if len(self.tasks) == 0:
			return

		map_t = {}
		
		name = "%d-%d.csv" % (int(self.bal_sim.time - self.bal_sim.interval), int(self.bal_sim.time))
		op = open(name, "w+")

		for task_ID in self.tasks:
			key = "%d-%d-%d-%d" % (int(self.bal_sim.time - self.bal_sim.interval), int(self.bal_sim.time), self.tasks[task_ID].job_ID, self.tasks[task_ID].task_ID)
			map_t[key] = (self.tasks[task_ID].CPU_usage, self.tasks[task_ID].mem_usage)

		keys = sorted(map_t.keys())

		for key in keys:
			op.write(("\t".join(key.split("-"))) + ("\t%f\t%f\n" % map_t[key]))

		op.close()
			

	def balance(self):
		
		cpu = 0.
		mem = 0.

		self.n_round = self.n_round + 1

		n_rem = 0
		for task_ID in list(self.tasks): # Remove finished tasks
			if self.tasks[task_ID].last_round < self.n_round:
				del self.tasks[task_ID]
				del self.hist[task_ID]
				n_rem = n_rem + 1
			else:
				self.tasks[task_ID].inc_age()
				self.hist[task_ID].append((self.tasks[task_ID].CPU_usage, self.tasks[task_ID].mem_usage))

		self.reset_stats()

		for mac in self.machines: # Calculates how much CPU and mem power is available

			obj = self.machines[mac]
			cpu = cpu + obj.capacity_CPU
			mem = mem + obj.capacity_memory


		cpu_task = 0.
		mem_task = 0.

		for task in self.tasks:

			obj = self.tasks[task]
			len_hist = len(self.hist[task])

			cpu_task = cpu_task + obj.CPU_usage # Calculates how much CPU and mem power is required by the tasks
			mem_task = mem_task + obj.mem_usage

			if len_hist == self.len_hist_max: # Print the trace of CPU and mem usage of some tasks
	
				if self.n_writes <= self.n_writes_lim:

					self.n_writes = self.n_writes + 1

					f = open(self.logtask % task, "w+")
	
					for tup in self.hist[task]:
						lst = self.hist[task]
						f.write("%f %f\n" % (tup[0], tup[1]))

					f.close()

				self.hist[task] = []	


		strng = '%f %f\n' % (cpu_task / cpu, mem_task / mem)
		
		self.logf.write(strng)
		#print strng 

		#self.__generate_output()

		self.total_tasks       = len(self.tasks)
		self.machines_not_used = len(self.machines)

		#self.tasks.clear()

	def add_machine_event(self, mac):
		if mac.event_type == mac.ADD_EVENT:
			self.machines[mac.machine_ID] = mac
		elif mac.event_type == mac.UPDATE_EVENT:
			if mac.machine_ID in self.machines:
				self.machines[mac.machine_ID].capacity_CPU    = mac.capacity_CPU
				self.machines[mac.machine_ID].capacity_memory = mac.capacity_memory
		else:
			del self.machines[mac.machine_ID]

	def add_task_usage(self, task):
		if task.getID() in self.tasks:

			if self.tasks[task.getID()].last_round == (self.n_round + 1):
				cpu = max(self.tasks[task.getID()].CPU_usage, task.CPU_usage)
				mem = max(self.tasks[task.getID()].mem_usage, task.mem_usage)
			else:
				cpu = task.CPU_usage
				mem = task.mem_usage
				
			self.tasks[task.getID()].CPU_usage = cpu
			self.tasks[task.getID()].mem_usage = mem
		else:
			self.tasks[task.getID()] = task
			self.hist[task.getID()]  = []

		task_obj            = self.tasks[task.getID()]
		task_obj.last_round = self.n_round + 1
