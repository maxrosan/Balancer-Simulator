
import io, time
import methods.loadbalacing
import numpypy as numpy
import math, random, Queue
import sys

class LoadBalancingAlgorithm(methods.loadbalacing.LoadBalacing):
	
	def __init__(self, prediction, migration):
		methods.loadbalacing.LoadBalacing.__init__(self)

		self.machines    = {}
		self.tasks       = {}
		self.tasks_input = {}

		self.prediction  = prediction
		self.migration   = migration


	def get_mac(self, mid):
		if mid == -1:
			return None
		return self.machines[mid]
	
	def get_task(self, taskId):
		return self.tasks[taskId]

	def migrate(self, task):
		get_mac(task.machine_ID).remove_task(task)

		task.move       = True
		task.mig_origin = task.machine_ID
		task.machine_ID = -1

	def add_machine_event(self, mac):

		if mac.event_type == mac.ADD_EVENT:
			self.machines[mac.machine_ID] = mac

		elif mac.event_type == mac.UPDATE_EVENT:

			self.machines[mac.machine_ID].capacity_CPU    = mac.capacity_CPU
			self.machines[mac.machine_ID].capacity_memory = mac.capacity_memory

		else:
			for task in self.machines[mac.machine_ID].tasks:
				self.migrate(self.tasks[task])

			del self.machines[mac.machine_ID]

	def add_task_usage(self, task):
		if task.getID() in self.tasks_input:
			self.tasks_input[task.getID()].CPU_usage_real = max(self.tasks_input[task.getID()].CPU_usage_real, task.CPU_usage_real)
			self.tasks_input[task.getID()].mem_usage_real = max(self.tasks_input[task.getID()].mem_usage_real, task.mem_usage_real)
		else:
			self.tasks_input[task.getID()] = task

	def remove_task(self, task_ID):
		task = self.get_task(task_ID)

		if task.machine_ID != -1:
			self.get_mac(task.machine_ID).remove_task(task)

		del self.tasks[task_ID]

	def add_new_task(self, task):
		pass

	def __add_new_task(self, task): # new task event
		self.prediction.calculate_prediction_for_new_task(task)
		self.add_new_task(task)

	def __calculate_prediction(self, task):
		self.prediction.calculate_prediction(task)

	def __must_migrate(self, old_task, new_task, machine):
		return self.migration.must_migrate(old_task, new_task, machine)

	def algorithm(self):
		pass

	def balance(self):

		self.n_round = self.n_round + 1

		self.reset_stats()
					
		# Remove tasks finished
		for task_ID in list(self.tasks):
			if not (task_ID in self.tasks_input):
				self.remove_task(task_ID)
				self.finished_tasks = self.finished_tasks + 1

		for task_ID in self.tasks_input:
			if not (task_ID in self.tasks): # new task coming

				task = self.tasks_input[task_ID]
				task.first_round = task.last_round = self.n_round
				self.__add_new_task(task)
				self.tasks[task_ID] = task

			else: # old task

				task        = self.get_task(task_ID)
				task_update = self.tasks_input[task_ID]
					
				task.inc_age()
				task.last_round = self.n_round
	
				self.__calculate_prediction(task_update)

				if self.__must_migrate(task, task_update, self.get_mac(task.machine_ID)):
					self.migrate(task)
				else:
					if task.machine_ID != -1:
						get_mac(task.machine_ID).remove_task(task)
						get_mac(task.machine_ID).add_task(task_update)

				task.CPU_usage = task_update.CPU_usage
				task.mem_usage = task_update.mem_usage
				task.CPU_usage_real = task_update.CPU_usage_real
				task.mem_usage_real = task_update.mem_usage_real
				


		s_time = time.time()

		self.algorithm()

		self.total_time = time.time() - s_time

		self.tasks_input.clear()

		self.__calc_usage()

		self.total_tasks              = len(self.tasks)
		self.SLA_breaks               = self.__count_SLAs()
		self.n_migrations             = self.__count_migrations()
		(self.task_mapped_successfully, self.task_failed_to_map) = self.__count_mapped()
		(self.machines_used, self.machines_not_used)             = self.__count_macs()
		self.task_new                 = self.__count_new_tasks()

	def __calc_usage(self):

		self.mac_usage.clear()

		usage_vec = []
		usage_cpu = []
		usage_mem = []

		for mac in self.machines:
			lst_tasks = []
			if self.machines[mac].n_tasks > 0:
				self.mac_usage[mac] = (self.machines[mac], lst_tasks)
				for task in self.machines[mac].tasks:
					lst_tasks.append(self.tasks[task])

				mac_obj = self.mac_usage[mac][0]
				usage_vec.append((mac_obj.CPU_usage_real * mac_obj.mem_usage_real) / (mac_obj.capacity_CPU * mac_obj.capacity_memory))
				usage_cpu.append(mac_obj.CPU_usage_real / mac_obj.capacity_CPU)
				usage_mem.append(mac_obj.mem_usage_real / mac_obj.capacity_memory)

		if len(usage_vec) > 0:
			self.usage_mean_per = numpy.mean(usage_vec)
			self.usage_stan_per = numpy.std(usage_vec)
			self.usage_CPU_mean = numpy.mean(usage_cpu)
			self.usage_mem_mean = numpy.mean(usage_mem)

	def __count_migrations(self):
		res = 0

		for task_ID in self.tasks:
			task = self.tasks[task_ID]
			if task.machine_ID != -1 and task.move and task.mig_origin != task.machine_ID:
				task.move       = False
				res             = res + 1
				task.mig_origin = -1

		return res

	def __count_macs(self):
		res_y = 0
		res_n = 0
		
		for mac_ID in self.machines:
			if self.machines[mac_ID].count_tasks() > 0:
				res_y = res_y + 1
			else:
				res_n = res_n + 1

		return (res_y, res_n)


	def __count_new_tasks(self):
		new_tasks = 0
		for task_ID in self.tasks:
			if self.tasks[task_ID].age_round == 0:
				new_tasks = new_tasks + 1
		return new_tasks

	def __count_SLAs(self):
		res = 0
		for mac_ID in self.machines:
			if self.machines[mac_ID].SLA_break():
				res = res + self.machines[mac_ID].n_tasks
		return res

	def __count_mapped(self):
		res_y = 0
		res_n = 0
		for task_ID in self.tasks:
			if self.tasks[task_ID].machine_ID == -1:
				res_n = res_n + 1
			else:
				res_y = res_y + 1
		return (res_y, res_n)
