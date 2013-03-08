import loadbalacing
import numpypy as numpy
import math, random, Queue, io

# RandomMethod selects a task randomly to run
#
class TasksStats(loadbalacing.LoadBalacing):

	def __init__(self, fileoutput):

		loadbalacing.LoadBalacing.__init__(self)

		self.tasks         = {}
		self.machines      = {}
		self.logf          = open(fileoutput, 'w+')
		self.hist          = {}

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

		for task_ID in list(self.tasks):
			if self.tasks[task_ID].last_round < self.n_round:
				del self.tasks[task_ID]
				del self.hist[task_ID]
			else:
				self.tasks[task_ID].inc_age()

		self.reset_stats()

#		for mac in self.machines:
#
#			obj = self.machines[mac]

#			cpu = cpu + obj.capacity_CPU
#			mem = mem + obj.capacity_memory


		#cpu_task = 0.
		#mem_task = 0.

		n_hists = 0
		max_hist = 0

		for task in self.tasks:

			obj = self.tasks[task]
			len_hist = len(self.hist[task])
			max_hist = max(len_hist, max_hist)	

			if len_hist >= 50:

				n_hists = n_hists + 1

				f = open("log/tasks/task." + task + ".log", "a+")

				for tup in self.hist[task]:
					f.write("%f %f\n" % tup)

				f.close()

			self.hist[task] = []

		print "n_hists = %d; max = %d" % (n_hists, max_hist)
				

		#	cpu_task = cpu_task + obj.CPU_usage
		#	mem_task = mem_task + obj.mem_usage

		#strng = '%f %f\n' % (cpu_task / cpu, mem_task / mem)
		
		#self.logf.write(strng)
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
			cpu = max(self.tasks[task.getID()].CPU_usage, task.CPU_usage)
			mem = max(self.tasks[task.getID()].mem_usage, task.mem_usage)
				
			self.tasks[task.getID()].CPU_usage = cpu
			self.tasks[task.getID()].mem_usage = mem
			
			self.hist[task.getID()].append((cpu, mem))
		else:
			self.tasks[task.getID()] = task
			self.hist[task.getID()]  = [(task.CPU_usage, task.mem_usage)]

		task_obj            = self.tasks[task.getID()]
		task_obj.last_round = self.n_round + 1
