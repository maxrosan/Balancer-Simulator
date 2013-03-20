
import binpackingmethod
import numpypy as numpy
import math, random, Queue

import threading, multiprocessing, time, sys

## FFD without prediction
class FFDMethod(binpackingmethod.BinPackingMethod):

	def __init__(self, threshold, w_cpu, w_mem, mac_sorted):
		binpackingmethod.BinPackingMethod.__init__(self, threshold)

		self.w_cpu      = w_cpu
		self.w_mem      = w_mem
		self.mac_sorted = mac_sorted

	def bin_packing(self, tasks, macs):

		def score_task(task):
			dcpu = self.w_cpu * task.CPU_usage
			dmem = self.w_mem * task.mem_usage

			return (dcpu + dmem)

		def score_mac(mac):
			return mac.free_CPU()

		tasks_sorted = sorted(tasks, key=lambda task_ID:score_task(self.tasks_state[task_ID]), reverse=True)

		if self.mac_sorted:
			macs_sorted  = sorted([mac for mac in macs if self.machines_state[mac].count_tasks() > 0], 
			 key=lambda mac_ID:score_mac(self.machines_state[mac_ID]), reverse=True) + \
			 sorted([mac for mac in macs if self.machines_state[mac].count_tasks() == 0],
			  key=lambda mac_ID:score_mac(self.machines_state[mac_ID]), reverse=True)
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
