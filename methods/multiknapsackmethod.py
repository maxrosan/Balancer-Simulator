import loadbalacing, random, usageclass
import numpy, math
#import multiprocessing as mp
import threading as thr

class MKThread(thr.Thread):
	
	def __init__(self, number, mac, tasks):
		thr.Thread.__init__(self)
		self.thread_id = number
		self.tasks = tasks
		self.mac = mac

	def run(self):
		MultiKnapsackMethod.run_dp(self.mac, self.tasks)

class MultiKnapsackMethod(loadbalacing.LoadBalacing):

	def __init__(self):
		loadbalacing.LoadBalacing.__init__(self)
		self.n_threads = 1

	@staticmethod
	def run_dp(mac_list, tasks_to_run):

		## sorting the machine in non-incresing order using the CPU capacity value
		mac_list = sorted(list(mac_list), key=lambda mac: mac.capacity_CPU, reverse=True)

		if len(tasks_to_run) == 0:
			return

		n = len(tasks_to_run)

		dp  = numpy.zeros(1001, float)
		lastAdded = numpy.zeros(1001, int)
		can = set([])

		for mac in mac_list:
			mem_cap = int(mac.capacity_memory * 1000)
			cpu_cap = 1.5 * mac.capacity_CPU

			dp.fill(-1000)
			lastAdded.fill(-1)
			can.clear()

			print "Processing %d w/ (%d, %f)" % (mac.machine_ID, mem_cap, cpu_cap)

			i = 0
			dp[0] = 0
			maxw = 0
			for task in tasks_to_run:
				mem_task = int(task.mem_usage * 1000)
				cpu_task = task.CPU_usage

				if mem_task == 0:
					mem_task = 1

				if not (task.task_ID in can):
					can.add(task.task_ID)
				else:
					continue

				for mem in reversed(range(mem_task, mem_cap + 1)):
					if dp[mem - mem_task] != -1000 and dp[mem] < (dp[mem - mem_task] + cpu_task):
						dp[mem] = dp[mem - mem_task] + cpu_task
						lastAdded[mem] = i
						maxw = max(maxw, mem)

				i = i + 1

			mem = maxw
			while lastAdded[mem] != -1:
				i = lastAdded[mem]
				task = tasks_to_run[i]
				mem_task = int(task.mem_usage * 1000)
				if mem_task == 0:
					mem_task = 1
				print mem, " ", task.task_ID	
				mem = mem - mem_task
			break

	
	def balance(self, machines_ready, tasks_to_run, tasks_constraints): 

		print "\nMulti Knapsack balacing"
		print "Balancear " + str(len(tasks_to_run)) + " tarefas em " + str(len(machines_ready)) + " maquinas"

		self.n_round = self.n_round + 1
	
		mac_list = list(machines_ready)
		tasks_list = list(tasks_to_run)

		self.reset_stats()

		threads = []
		tasks_div = len(tasks_to_run) / self.n_threads
		mac_div   = len(mac_list) / self.n_threads
		#for i in range(0, self.n_threads):
		#	print "Processing ", i
		#	t = MKThread(i, mac_list[mac_div*i:mac_div*(i+1)], tasks_list[tasks_div*i:tasks_div*(i + 1)])
		#	t.start()
		#	threads.append(t)

		

		MultiKnapsackMethod.run_dp(list(mac_list), list(tasks_to_run))
		#XXX: tem que verificar o resto ainda

		#for t in threads:
		#	t.join()
	
		return
