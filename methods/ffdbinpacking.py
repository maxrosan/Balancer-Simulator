
import methods.loadbalancingalgorithm
import numpypy as numpy
import math, random, Queue

import threading, multiprocessing, time, sys

class FFDBinPacking(methods.loadbalancingalgorithm.LoadBalancingAlgorithm):
	
	def __init__(self, prediction, migration, mac_key_sort, task_key_sort, mac_sorted):

		methods.loadbalancingalgorithm.LoadBalancingAlgorithm.__init__(self, prediction, migration)

		self.mac_key_sort = mac_key_sort
		self.task_key_sort = task_key_sort
		self.mac_sorted = mac_sorted

	def add_new_task(self, task):
		pass

	def algorithm(self):

		tasks_sorted = sorted([task_ID for task_ID in self.tasks if self.get_task(task_ID).machine_ID == -1],
		  key=lambda task_ID: self.task_key_sort(self.tasks[task_ID]), reverse=True)

		macs = list(self.machines)

		if self.mac_sorted:
			macs_sorted  = sorted([mac for mac in macs if self.machines[mac].count_tasks() > 0], 
			 key=lambda mac_ID: self.mac_key_sort(self.machines[mac_ID]), reverse=True) + \
			 sorted([mac for mac in macs if self.machines[mac].count_tasks() == 0],
			  key=lambda mac_ID: self.mac_key_sort(self.machines[mac_ID]), reverse=True)
		else:
			macs_sorted = [mac for mac in macs if self.machines[mac].count_tasks() > 0] + \
			              [mac for mac in macs if self.machines[mac].count_tasks() == 0]

		for task in tasks_sorted:
			for mac in macs_sorted:
				if self.machines[mac].can_run(self.tasks[task]):

					obj = self.tasks[task]
					obj.machine_ID = mac

					self.machines[mac].add_task(obj)

					break
