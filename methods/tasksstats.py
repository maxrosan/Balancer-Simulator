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

	def balance(self):
		
		cpu = 0.
		mem = 0.

		self.n_round = self.n_round + 1

		self.reset_stats()

		for mac in self.machines:

			obj = self.machines[mac]

			cpu = cpu + obj.capacity_CPU
			mem = mem + obj.capacity_memory


		cpu_task = 0.
		mem_task = 0.

		for task in self.tasks:

			obj = self.tasks[task]

			cpu_task = cpu_task + obj.CPU_usage
			mem_task = mem_task + obj.mem_usage

		strng = '%f %f\n' % (cpu_task / cpu, mem_task / mem)
		
		self.logf.write(strng)
		print strng 

		self.tasks.clear()

		self.total_tasks  = len(self.tasks)

	def add_machine_event(self, mac):
		if mac.event_type == mac.ADD_EVENT:
			self.machines[mac.machine_ID] = mac
		elif mac.event_type == mac.UPDATE_EVENT:
			self.machines[mac.machine_ID].capacity_CPU    = mac.capacity_CPU
			self.machines[mac.machine_ID].capacity_memory = mac.capacity_memory
		else:
			del self.machines[mac.machine_ID]

	def add_task_usage(self, task):
		self.tasks[task.getID()] = task
