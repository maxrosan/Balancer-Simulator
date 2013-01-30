

import loadbalacing, random, usageclass

# RandomMethod selects a task randomly to run
#
class RandomMethod(loadbalacing.LoadBalacing):

	def __init__(self):
		loadbalacing.LoadBalacing.__init__(self)
		random.seed()
		self.max_runs = 10 # Maximum number of tries that the balancer does to pick a server for the task
	
	def balance(self, machines_ready, tasks_to_run, tasks_constraints): 

		print "\nRandom balacing"
		print "Balancear " + str(len(tasks_to_run)) + " tarefas em " + str(len(machines_ready)) + " maquinas"

		self.n_round = self.n_round + 1
		
		#mac_list = sorted(list(machines_ready), key=lambda mac: mac.capacity_CPU, reverse=True)

		self.reset_stats()	
		mac_list = list(machines_ready)

		for task in tasks_to_run:
			nruns = 0
			selected = False
			
			while (not selected) and (nruns < self.max_runs):
				nruns = nruns + 1
				mac_selected = mac_list[random.randint(0, len(mac_list)-1)] # select a server randomly
				count_mac = False

				if not (mac_selected.machine_ID in self.mac_usage): # check if server had been used before
					self.mac_usage[mac_selected.machine_ID] = usageclass.UsageClass(mac_selected.capacity_CPU, mac_selected.capacity_memory)
					count_mac = True

				if self.mac_usage[mac_selected.machine_ID].inc(task.CPU_usage, task.mem_usage): # check if the server is able to run the task
					selected = True
					self.task_mapped_successfully = self.task_mapped_successfully + 1 # count the task as executed
					if count_mac:
						self.machines_used = self.machines_used + 1 # count the server as used if the task here is the first one that machine runs

			if not selected:
				self.task_failed_to_map = self.task_failed_to_map + 1

		
		self.machines_not_used = len(mac_list) - self.machines_used
			#print "%d/%d(%.5f, %.5f) em mac %d (cpu = %.5f, mem = %.5f)" % (task.job_ID, task.task_ID, task.CPU_usage, task.mem_usage,
			#	mac_selected.machine_ID, mac_selected.capacity_CPU, mac_selected.capacity_memory)
