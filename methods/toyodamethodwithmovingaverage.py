
import toyodamethod
import numpypy as numpy
import math, random, Queue

import threading, multiprocessing, time, sys

class ToyodaMethodWithMovingAverage(toyodamethod.ToyodaMethod):

	def __init__(self, threshold, w_cpu, w_mem, n_entries):
		self.__init__(self, threshold, w_cpu, w_mem)

		self.hist_usage = {}
		self.n_entries  = n_entries

	def removePrediction(self, task_ID):
		del self.hist_usage[task_ID]

	def calculatePrediction(self):

		print "Calculating moving average prediction"
		
		for task_ID in self.tasks_input:
		
			if not (task_ID in self.hist_usage):
				self.hist_usage[task_ID] = []
			
			obj = self.tasks_input[task_ID]
			len_lst = len(self.hist_usage[task_ID])
			if len_lst >= self.n_entries:
				obj.CPU_usage = sum([tup[0] for tup in self.hist_usage[-self.n_entries:]])/float(self.n_entries)
				obj.mem_usage = sum([tup[1] for tup in self.hist_usage[-self.n_entries:]])/float(self.n_entries)
			elif len_lst > 1:
				obj.CPU_usage = sum([tup[0] for tup in self.hist_usage])/float(len_lst)
				obj.mem_usage = sum([tup[1] for tup in self.hist_usage])/float(len_lst)
			else:
				obj.CPU_usage = obj.CPU_usage_real * 1.3
				obj.mem_usage = obj.mem_usage_real * 1.3

			self.hist_usage[task_ID].append((obj.CPU_usage_real, obj.mem_usage_real))

		print "Prediction calculated"
