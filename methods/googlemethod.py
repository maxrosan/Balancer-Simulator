import loadbalacing
import numpypy as numpy
import math, random, Queue, io, operator

class GoogleMethod(loadbalacing.LoadBalacing):

	def __init__(self):
		loadbalacing.LoadBalacing.__init__(self)

		self.machines_state = {}
		self.tasks_input    = {}
		self.tasks_state    = {}

	def __count_SLAs(self):
		res = 0
		for mac_ID in self.machines_state:
			if self.machines_state[mac_ID].SLA_break():
				res = res + self.machines_state[mac_ID].n_tasks
		return res

	def balance(self):

		n_migrations = 0

		self.n_round = self.n_round + 1

		for task_ID in list(self.tasks_state):
			if not (task_ID in self.tasks_input):
				task = self.tasks_state[task_ID]
				if task.machine_ID != -1:
					self.machines_state[task.machine_ID].remove_task(task)
				del self.tasks_state[task_ID]

		for task_ID in self.tasks_input:
			if task_ID in self.tasks_state:
				if self.tasks_state[task_ID].machine_ID != self.tasks_input[task_ID].machine_ID:
					if self.tasks_state[task_ID].machine_ID != -1:
						n_migrations = n_migrations + 1
						self.machines_state[self.tasks_state[task_ID].machine_ID].remove_task(self.tasks_state[task_ID])
					self.machines_state[self.tasks_input[task_ID].machine_ID].add_task(self.tasks_input[task_ID])
			else:				
				self.machines_state[self.tasks_input[task_ID].machine_ID].add_task(self.tasks_input[task_ID])

			self.tasks_state[task_ID] = self.tasks_input[task_ID]

		usage_vec        = []
		usage_cpu_vec    = []
		usage_mem_vec    = []
		
		self.mac_usage.clear()
		
		for mac_ID in self.machines_state:
			usage     = 0.
			usage_cpu = 0.
			usage_mem = 0.

			lst_tasks = []
			self.mac_usage[mac_ID] = (self.machines_state[mac_ID], lst_tasks)

			self.machines_state[mac_ID].calculate_consumption(self.tasks_state)

			for task_ID in self.machines_state[mac_ID].tasks:
				self.mac_usage[mac_ID][1].append(self.tasks_state[task_ID])

				usage     = usage + self.tasks_state[task_ID].CPU_usage_real * self.tasks_state[task_ID].mem_usage_real
				usage_cpu = usage_cpu + self.tasks_state[task_ID].CPU_usage_real
				usage_mem = usage_mem + self.tasks_state[task_ID].mem_usage_real

			usage     = usage / (self.machines_state[mac_ID].capacity_CPU * self.machines_state[mac_ID].capacity_memory)
			usage_cpu = usage_cpu / self.machines_state[mac_ID].capacity_CPU
			usage_mem = usage_mem / self.machines_state[mac_ID].capacity_memory

			usage_vec.append(usage)
			usage_cpu_vec.append(usage_cpu)
			usage_mem_vec.append(usage_mem)

		self.tasks_input.clear()
		

		self.usage_mean_per           = numpy.mean(usage_vec)
		self.usage_stan_per           = numpy.std(usage_vec)
		self.usage_CPU_mean           = numpy.mean(usage_cpu)
		self.usage_mem_mean           = numpy.mean(usage_mem)
		self.total_tasks              = len(self.tasks_state)
		self.SLA_breaks               = self.__count_SLAs()
		self.n_migrations             = n_migrations
		self.task_failed_to_map       = len([task_ID for task_ID in self.tasks_state if self.tasks_state[task_ID].machine_ID == -1])
		self.task_mapped_successfully = self.total_tasks - self.task_failed_to_map
		(self.machines_used, self.machines_not_used) = self.__count_macs()
 
	def __count_macs(self):
		res_y = 0
		res_n = 0
		
		for mac_ID in self.machines_state:
			if self.machines_state[mac_ID].count_tasks() > 0:
				res_y = res_y + 1
			else:
				res_n = res_n + 1

		return (res_y, res_n)

	def add_machine_event(self, mac):
		if mac.event_type == mac.ADD_EVENT:
			self.machines_state[mac.machine_ID] = mac
		elif mac.event_type == mac.UPDATE_EVENT:
			self.machines_state[mac.machine_ID].capacity_CPU    = mac.capacity_CPU
			self.machines_state[mac.machine_ID].capacity_memory = mac.capacity_memory
		else:
			for task in self.machines_state[mac.machine_ID].tasks:
				self.tasks_state[task].machine_ID = -1

			del self.machines_state[mac.machine_ID]	

	def add_task_usage(self, task):
		if task.getID() in self.tasks_input:
			self.tasks_input[task.getID()].CPU_usage_real = max(self.tasks_input[task.getID()].CPU_usage_real, task.CPU_usage_real)
			self.tasks_input[task.getID()].mem_usage_real = max(self.tasks_input[task.getID()].mem_usage_real, task.mem_usage_real)
			self.tasks_input[task.getID()].machine_ID     = task.machine_trace
		else:
			self.tasks_input[task.getID()]                = task
			self.tasks_input[task.getID()].machine_ID     = task.machine_trace
