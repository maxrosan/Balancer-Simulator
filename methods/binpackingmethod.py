
import loadbalacing
import numpypy as numpy
import math, random, Queue

import threading, multiprocessing, time, sys

class BinPackingMethod(loadbalacing.LoadBalacing):

	def __init__(self, threshold):
		loadbalacing.LoadBalacing.__init__(self)

		self.machines_state = {}
		self.tasks_state    = {}
		self.tasks_input    = {}

		self.threshold_migration = threshold

	def bin_packing(self, tasks, macs):
		pass

	def calculatePrediction(self):

		for task_ID in self.tasks_input:
			self.tasks_input[task_ID].CPU_usage = self.tasks_input[task_ID].CPU_usage_real
			self.tasks_input[task_ID].mem_usage = self.tasks_input[task_ID].mem_usage_real


	def removePrediction(self, task_ID):
		pass


	def __update_tasks(self):

		print "Updating"

		for task_ID in list(self.tasks_state):
			task = self.tasks_state[task_ID]
			if not (task_ID in self.tasks_input):
				if task.machine_ID != -1:
					self.machines_state[task.machine_ID].remove_task(self.tasks_state[task_ID])			
				self.removePrediction(task_ID)
				del self.tasks_state[task_ID]

		self.calculatePrediction()

		for task_ID in self.tasks_input:

			if not (task_ID in self.tasks_state):
				task = self.tasks_state[task_ID] = self.tasks_input[task_ID]
				task.first_round = (self.n_round + 1)
				task.last_round  = (self.n_round + 1)
			else:
				new_task = self.tasks_input[task_ID]
				old_task = self.tasks_state[task_ID]
			
				old_task.inc_age()
				old_task.last_round = self.n_round + 1
				from_mach = old_task.machine_ID

				if old_task.machine_ID != -1:

					self.machines_state[from_mach].remove_task(old_task)
					old_task.machine_ID = -1

					if old_task.age_round <= self.threshold_migration:
						if not self.machines_state[from_mach].can_run(new_task):
							self.migrate(old_task)
						else:
							old_task.move       = False
							old_task.machine_ID = from_mach

							old_task.CPU_usage_real = new_task.CPU_usage_real
							old_task.mem_usage_real = new_task.mem_usage_real
							old_task.CPU_usage      = new_task.CPU_usage
							old_task.mem_usage      = new_task.mem_usage	

							self.machines_state[from_mach].add_task(old_task)
					else:
						old_task.age_round = 1
						self.migrate(old_task)

				old_task.CPU_usage = new_task.CPU_usage
				old_task.mem_usage = new_task.mem_usage
				old_task.CPU_usage_real = new_task.CPU_usage_real
				old_task.mem_usage_real = new_task.mem_usage_real

		self.tasks_input.clear()

	def migrate(self, task):
		task.move = True
		task.mig_origin = task.machine_ID
		task.machine_ID = -1

	def balance(self):

		self.__update_tasks()			

		self.n_round = self.n_round + 1

		self.reset_stats()
		self.task_new = self.__count_new_tasks()

		## Bin-packing
		
		print "Running BP"

		tasks  = [task_ID for task_ID in self.tasks_state if self.tasks_state[task_ID].machine_ID == -1]
		macs   = list(self.machines_state)
		s_time = time.time()

		self.bin_packing(tasks, macs)

		print "OK [ Running BP ]"

		##

		self.total_time = time.time() - s_time

		self.__calc_usage()

		self.total_tasks              = len(self.tasks_state)
		self.SLA_breaks               = self.__count_SLAs()
		self.n_migrations             = self.__count_migrations()

		(self.task_mapped_successfully, self.task_failed_to_map) = self.__count_mapped()
		(self.machines_used, self.machines_not_used)             = self.__count_macs()

	def add_task_usage(self, task):
		if task.getID() in self.tasks_input:
			self.tasks_input[task.getID()].CPU_usage_real = max(self.tasks_input[task.getID()].CPU_usage_real, task.CPU_usage_real)
			self.tasks_input[task.getID()].mem_usage_real = max(self.tasks_input[task.getID()].mem_usage_real, task.mem_usage_real)
		else:
			self.tasks_input[task.getID()]                = task

	def add_machine_event(self, mac):
		if mac.event_type == mac.ADD_EVENT:
			self.machines_state[mac.machine_ID] = mac
		elif mac.event_type == mac.UPDATE_EVENT:

			if self.machines_state[mac.machine_ID].capacity_CPU > mac.capacity_CPU or \
			  self.machines_state[mac.machine_ID].capacity_memory > mac.capacity_memory:
				for task in self.machines_state[mac.machine_ID].tasks:
					self.migrate(self.tasks_state[task])
					self.machines_state[mac.machine_ID].remove_task(self.tasks_state[task])

			self.machines_state[mac.machine_ID].capacity_CPU    = mac.capacity_CPU
			self.machines_state[mac.machine_ID].capacity_memory = mac.capacity_memory

		else:
			for task in self.machines_state[mac.machine_ID].tasks:
				self.migrate(self.tasks_state[task])

			del self.machines_state[mac.machine_ID]

	def __count_new_tasks(self):
		new_tasks = 0
		for task_ID in self.tasks_state:
			if self.tasks_state[task_ID].age_round == 0:
				new_tasks = new_tasks + 1
		return new_tasks

	def __count_SLAs(self):
		res = 0
		for mac_ID in self.machines_state:
			if self.machines_state[mac_ID].SLA_break():
				res = res + self.machines_state[mac_ID].n_tasks
		return res

	def __count_mapped(self):
		res_y = 0
		res_n = 0
		for task_ID in self.tasks_state:
			if self.tasks_state[task_ID].machine_ID == -1:
				res_n = res_n + 1
			else:
				res_y = res_y + 1
		return (res_y, res_n)

	def __count_macs(self):
		res_y = 0
		res_n = 0
		
		for mac_ID in self.machines_state:
			if self.machines_state[mac_ID].count_tasks() > 0:
				res_y = res_y + 1
			else:
				res_n = res_n + 1

		return (res_y, res_n)

	def __count_migrations(self):
		res = 0

		for task_ID in self.tasks_state:
			task = self.tasks_state[task_ID]
			if task.machine_ID != -1 and task.move and task.mig_origin != task.machine_ID:
				task.move       = False
				res             = res + 1
				task.mig_origin = -1

		return res

	def __calc_usage(self):
		print "Printing tasks......",

		self.mac_usage.clear()

		usage_vec = []
		usage_cpu = []
		usage_mem = []

		for mac in self.machines_state:
			lst_tasks = []
			if self.machines_state[mac].n_tasks > 0:
				self.mac_usage[mac] = (self.machines_state[mac], lst_tasks)
				for task in self.machines_state[mac].tasks:
					lst_tasks.append(self.tasks_state[task])

				mac_obj = self.mac_usage[mac][0]
				usage_vec.append((mac_obj.CPU_usage_real * mac_obj.mem_usage_real) / (mac_obj.capacity_CPU * mac_obj.capacity_memory))
				usage_cpu.append(mac_obj.CPU_usage_real / mac_obj.capacity_CPU)
				usage_mem.append(mac_obj.mem_usage_real / mac_obj.capacity_memory)

		if len(usage_vec) > 0:
			self.usage_mean_per = numpy.mean(usage_vec)
			self.usage_stan_per = numpy.std(usage_vec)
			self.usage_CPU_mean = numpy.mean(usage_cpu)
			self.usage_mem_mean = numpy.mean(usage_mem)

		print "OK"
