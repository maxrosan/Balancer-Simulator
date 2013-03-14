
import toyodamethod
import numpypy as numpy
import math, random, Queue

import threading, multiprocessing, time, sys

class ToyodaMethodWithMovingAverage(toyodamethod.ToyodaMethod):

	def __init__(self, threshold, w_cpu, w_mem, n_entries):
		toyodamethod.ToyodaMethod.__init__(self, threshold, w_cpu, w_mem)

		self.hist_usage = {}
		self.n_entries  = n_entries

	def removePrediction(self, task_ID):
		del self.hist_usage[task_ID]

	def beforeBalancing(self):

		print "Before balancing"

		for mac_ID in self.machines_state:
			mac = self.machines_state[mac_ID]
			if mac.SLA_breaks():
				tasks = sorted([self.tasks_state[task_ID] for task_ID in mac.tasks],
					key=lambda task: task.CPU_usage*task.mem_usage, reverse=True)

				task_i = 0
				len_tasks = len(tasks)
				while mac.SLA_breaks() and mac.count_tasks() > 0:
					mac.remove_task(tasks[task_i])
					self.migrate(tasks[task_i])
					task_i = task_i + 1

		print "OK"
			

	def calculatePrediction(self):

		print "Calculating moving average prediction"
		
		for task_ID in self.tasks_input:
		
			if not (task_ID in self.hist_usage):
				self.hist_usage[task_ID] = []
			
			obj = self.tasks_input[task_ID]
			len_lst = len(self.hist_usage[task_ID])
			if len_lst >= self.n_entries:
				obj.CPU_usage = sum([tup[0] for tup in self.hist_usage[task_ID][-self.n_entries:]])/float(self.n_entries)
				obj.mem_usage = sum([tup[1] for tup in self.hist_usage[task_ID][-self.n_entries:]])/float(self.n_entries)
			elif len_lst > 1:
				obj.CPU_usage = sum([tup[0] for tup in self.hist_usage[task_ID]])/float(len_lst)
				obj.mem_usage = sum([tup[1] for tup in self.hist_usage[task_ID]])/float(len_lst)
			else:
				obj.CPU_usage = min(obj.CPU_usage_real * 1.2, 1.)
				obj.mem_usage = min(obj.mem_usage_real * 1.2, 1.)

			self.hist_usage[task_ID].append((obj.CPU_usage_real, obj.mem_usage_real))

		print "Prediction calculated"
