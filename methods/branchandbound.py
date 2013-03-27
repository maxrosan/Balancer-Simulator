
import binpackingmethod
import numpypy as numpy
import math, random, Queue

import threading, multiprocessing, time, sys

class BranchAndBoundMethod(binpackingmethod.BinPackingMethod):

	def __init__(self, threshold):
		binpackingmethod.BinPackingMethod.__init__(self, threshold)

		self.Gv = 0

	def __bbm(self, tasks, mac, i, M, N, value):
		if M > value:
			return 0
		elif i == N:
			return M
		elif (((N - i - 1) + M) * 0.7) > self.Gv:
			x = self.__bbm(tasks, mac, i+1, M + tasks[i].CPU_usage*mac.free_CPU() + tasks[i].mem_usage*mac.free_mem(), N, value)
			y = self.__bbm(tasks, mac, i+1, M, N, value)

			mx = max(x, y)
			self.Gv = max(self.Gv, mx)

			return mx
		else:
			return 0

	def bin_packing(self, tasks, macs):

		self.Gv = 0

		tasks_lst = sorted([self.tasks_state[task_ID] for task_ID in tasks], key=lambda task: (1. + task.CPU_usage)*(1. + task.mem_usage), reverse=True)
		print self.__bbm(tasks_lst, self.machines_state[macs[0]], 0, 0., len(tasks_lst), self.machines_state[macs[0]].capacity_CPU * self.machines_state[macs[0]].capacity_memory)

		if len(tasks_lst) == 0:
			exit()
