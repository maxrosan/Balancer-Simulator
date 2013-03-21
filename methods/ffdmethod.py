
import binpackingmethod
import numpypy as numpy
import math, random, Queue

import threading, multiprocessing, time, sys

## FFD without prediction
class FFDMethod(binpackingmethod.BinPackingMethod):

	def __init__(self, threshold, , mac_sorted):
		binpackingmethod.BinPackingMethod.__init__(self, threshold)

		self.mac_key_sort  = mac_key_sort
		self.task_key_sort = task_key_sort
		self.mac_sorted    = mac_sorted

	def bin_packing(self, tasks, macs):

		tasks_sorted = sorted(tasks, key=lambda task_ID: self.task_key_sort(self.tasks_state[task_ID]), reverse=True)

		if self.mac_sorted:
			macs_sorted  = sorted([mac for mac in macs if self.machines_state[mac].count_tasks() > 0], 
			 key=lambda mac_ID: self.task_key_sort(self.machines_state[mac_ID]), reverse=True) + \
			 sorted([mac for mac in macs if self.machines_state[mac].count_tasks() == 0],
			  key=lambda mac_ID: self.task_key_sort(self.machines_state[mac_ID]), reverse=True)
		else:
			macs_sorted = [mac for mac in macs if self.machines_state[mac].count_tasks() > 0] + \
			              [mac for mac in macs if self.machines_state[mac].count_tasks() == 0]

		for task in tasks_sorted:
			for mac in macs_sorted:
				if self.machines_state[mac].can_run(self.tasks_state[task]):

					obj            = self.tasks_state[task]
					obj.machine_ID = mac

					self.machines_state[mac].add_task(obj)

					break
