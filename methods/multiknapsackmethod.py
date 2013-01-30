import loadbalacing, random, usageclass
import numpy
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
		self.n_threads = 2

	@staticmethod
	def run_dp(mac_list, tasks_to_run):

		## sorting the machine in non-incresing order using the CPU capacity value
		mac_list = sorted(list(mac_list), key=lambda mac: mac.capacity_CPU, reverse=True)

		if len(tasks_to_run) == 0:
			return

		for mac in mac_list:
			cpu_cap = mac.capacity_CPU * 1000
			mem_cap = mac.capacity_memory * 1000

			dp  = numpy.zeros((1001,1001), float)
			par = numpy.zeros((1001,1001), int)

			print "Processing ", mac.machine_ID

			for task in tasks_to_run:
				cpu_task = int(1000 * task.CPU_usage)
				mem_task = int(1000 * task.mem_usage)
				gain_task = task.CPU_usage
				
				for cpu in reversed(range(cpu_task, 1001)):
					for mem in reversed(range(mem_task, 1001)):
						dp[cpu][mem] = max(dp[cpu - cpu_task][mem - mem_task] + gain_task, dp[cpu][mem])
						

	
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
		for i in range(0, self.n_threads):
			print "Processing ", i

			t = MKThread(i, mac_list[mac_div*i:mac_div*(i+1)], tasks_list[tasks_div*i:tasks_div*(i + 1)])
			t.start()
			threads.append(t)

		#XXX: tem que verificar o resto ainda

		for t in threads:
			t.join()
	
		return
